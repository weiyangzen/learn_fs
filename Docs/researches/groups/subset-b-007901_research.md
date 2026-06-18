# subset-b-007901 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crawler.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crawler.py

## Purpose
This module tests `allmydata.storage.crawler.ShareCrawler` against a real `StorageServer` share directory. It verifies that crawler subclasses enumerate bucket directories, persist and resume prefix/cycle progress, respect service lifecycle scheduling, expose progress/state before and during work, and can stop themselves after a single cycle.

## Important APIs, types, and functions
- `BucketEnumeratingCrawler`, `PacedCrawler`, `ConsumingCrawler`, and `OneShotCrawler` are local `ShareCrawler` subclasses used to exercise extension hooks: `process_bucket`, `finished_cycle`, and `yielding`.
- `Basic.setUp` and `tearDown` manage a Twisted `MultiService` parent, so storage servers and crawler services run under real service lifecycle semantics.
- `Basic.write` allocates one storage bucket through `StorageServer.allocate_buckets`, writes share data, closes the writer, and returns the base32 storage index string via `si_b2a`.
- Tests call `load_state`, `save_state`, `start_current_prefix`, `get_state`, `get_progress`, `setServiceParent`, and `disownServiceParent` on crawler instances.

## Control flow
The tests create deterministic storage indexes from integer seeds and sometimes mutate the final byte to place multiple buckets under one prefix directory. `test_immediate` drives crawling synchronously with `start_current_prefix` and confirms that a completed cycle resets the statefile to the beginning. `test_service` attaches a crawler to the service tree and waits on a Deferred fired by `finished_cycle`. `test_paced` forces `TimeSliceExceeded` in the middle and end of bucket processing, manually saves state, then constructs new crawler instances to verify resume behavior. `test_paced_service` exercises the scheduled path and checks progress while the crawler yields. `test_empty_subclass` runs the base crawler for coverage of no-op hooks, and `test_oneshot` confirms a crawler can detach from its parent after the first completed cycle.

## State and persistence behavior
State lives in the crawler statefile under each test-specific basedir. The tests inspect `last-complete-prefix`, `current-cycle`, `last-cycle-finished`, progress booleans, sleep timers, and remaining wait/sleep times. The most important persistence behavior is resumability after `TimeSliceExceeded`: a crawler that saves state mid-cycle must let a fresh process continue without duplicating or skipping buckets. The tests also validate that a fully completed cycle resets traversal state so later crawlers start from the beginning.

## Dependencies and integration points
The module depends on Twisted Trial, Twisted services, Foolscap `eventually`/`fireEventually`, Tahoe `StorageServer`, `ShareCrawler`, storage-index hash helpers, filesystem helpers, and polling/stall utilities from Tahoe tests. It integrates crawler behavior with actual storage server layout rather than mocking the share tree.

## Risks
Timing-sensitive assertions in `test_paced_service` depend on deterministic share ordering and expected completion percentage after six buckets. The disabled CPU-usage test documents that wall-clock and host load make strict CPU throttling tests unreliable. Resume correctness is also fragile around boundaries where a timeslice expires inside `process_bucket` versus immediately after a bucket.

## Test signals
Useful regression signals are complete bucket-set equality, correct progress flags before first tick and during a yield, persisted resume across new crawler instances, timer/sleep fields after service-driven completion, base-class cycle completion, and one-shot shutdown with no further counter increments after disowning the service parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crawler.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crypto.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crypto.py

## Purpose
This module tests Tahoe-LAFS cryptographic compatibility and validation wrappers for AES, Ed25519, RSA, and small crypto utilities. A major theme is preserving compatibility with old `pycryptopp` serialized keys, signatures, and AES stream behavior after migration to `cryptography`.

## Important APIs, types, and functions
- `TestRegression` loads legacy key and signature fixtures from `test/data` and exercises `aes.create_encryptor`, `aes.create_decryptor`, `aes.encrypt_data`, `aes.decrypt_data`, `ed25519.signing_keypair_from_string`, `ed25519.verifying_key_from_string`, `ed25519.sign_data`, `ed25519.verify_signature`, and `rsa.create_signing_keypair_from_string`.
- `TestEd25519` covers key generation, serialization/deserialization, signing, verification, and type validation.
- `TestRsa` covers RSA key generation, DER serialization, deserialization, signing, verification, bad signatures, and key-object validation.
- `TestUtil` covers `remove_prefix` and `BadPrefixError`.

## Control flow
Class-level fixture loading reads base64-encoded RSA data once from `RESOURCE_DIR`. The AES regression tests compare ciphertext bytes from known inputs with and without IV, including chunked processing that must match one-shot processing. Ed25519 regression reconstructs old private/public strings, compares derived and explicit public keys, checks deterministic legacy signature compatibility, and verifies both old and new signatures. RSA regression accepts a 2048-bit legacy private key and rejects legacy 1024-bit and 32768-bit keys. Later tests generate fresh keys and check round-trip serialization plus negative input validation.

## State and persistence behavior
The module itself has no persistent application state beyond fixture files. The important serialized state is cryptographic material: legacy pycryptopp RSA private/public bytes, signatures, Ed25519 string encodings, DER-encoded RSA keys, AES keys, and IVs. Tests assert byte-for-byte compatibility for serialized keys and encrypted/signature outputs where compatibility is required.

## Dependencies and integration points
Dependencies include `base64`, `binascii`, Twisted `FilePath`, Tahoe crypto modules, and Tahoe crypto error types. Integration is focused on Tahoe's compatibility surface: code that reads existing caps, mutable keys, or migrated nodes depends on these wrappers accepting old formats while rejecting insecure or malformed data.

## Risks
Cryptographic compatibility tests are intentionally byte-exact; changing cipher mode, counter initialization, key prefix parsing, serialization prefix, or RSA size policy can break stored data compatibility. Some negative tests assert exception message substrings, so error text changes can cause failures even when exception types remain correct. `TestRsa.test_sign_invalid_pubkey` creates a 1024-bit key even though legacy deserialization rejects tiny keys, so generated-key policy changes may require test updates.

## Test signals
Strong signals include Niels Ferguson AES known-answer vectors, short and long AES process compatibility, old Ed25519 and RSA fixture verification, key-size rejection boundaries, type checks for bytes-only data, invalid key-object checks, RSA bad-signature failure, and prefix-removal edge cases including empty, whole-string, bad, and partial prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_crypto.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deepcheck.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deepcheck.py

## Purpose
This module tests Tahoe-LAFS object check, repair, deep-check, deep-stats, manifest, CLI, and web API behavior across healthy, damaged, literal, mutable, immutable, directory, and large traversal scenarios. It exercises both programmatic node APIs and HTTP/CLI surfaces.

## Important APIs, types, and functions
- `run_cli` adapts `run_cli_unicode` to the existing varargs test style.
- `MutableChecker` tests mutable file web check and repair flows after corrupting or deleting shares.
- `DeepCheckBase` provides helpers for JSON web calls, streamed JSON parsing, operation-handle polling, and slow asynchronous web operations.
- `DeepCheckWebGood` constructs a mixed healthy tree and verifies `check`, `check_and_repair`, `start_deep_check`, `start_deep_check_and_repair`, `start_deep_stats`, stream manifest, web JSON, and CLI manifest/stats variants.
- `DeepCheckWebBad` builds a damaged tree and verifies healthy, missing-share, corrupt-share, and unrecoverable classifications with and without verification.
- `Large` checks that streaming deep-check over hundreds of literal files avoids Deferred tail-recursion overflow.

## Control flow
Healthy tests build a root directory containing mutable, CHK immutable, LIT files, empty/tiny LIT directories, and a loop back to root. The flow runs local stats, stream-manifest parsing, local node checks, web checks for all combinations of `verify` and `repair`, deep-check operations through operation handles, info pages, and CLI manifest/stats commands. The bad-tree flow builds mutable and large files for good, missing-share, corrupt-share, and unrecoverable cases, plus a broken subdirectory whose shares are mostly deleted. It compares non-verify checks, which do not detect corrupt shares, with verify checks, which do. Large traversal creates one CHK file plus 399 LIT children and validates streamed result count.

## State and persistence behavior
Test state is stored in in-memory attributes such as `root`, `mutable`, `large`, URI fields, and `nodes`, with persistent shares created in per-test basedirs by `GridTestMixin`. Damage is persisted by deleting shares, corrupting share data with `_corrupt_mutable_share_data`, and invoking `debug corrupt-share` through the CLI. Web operations persist status under `operations/<ophandle>` until the helper polls `finished`. Deep checks use `Monitor` objects, including explicit cancellation that must produce `OperationCancelledError`.

## Dependencies and integration points
The module depends on Twisted Deferreds and `inlineCallbacks`, Tahoe upload and mutable publishing APIs, mutable error types, check-result interfaces, `Monitor`, URI classes, grid/no-network test infrastructure, web HTTP helpers, CLI helpers, base32/idlib formatting, and JSON parsing. It is a broad integration test spanning node APIs, storage shares, web API query parameters, operation handles, streaming JSON protocols, and command-line output formats.

## Risks
Many assertions pin exact counters, output text, and CLI formatting, so changes to traversal semantics or presentation can require coordinated test updates. Corruption detection intentionally differs between verify and non-verify paths; regressions can hide if a code path starts reading too much or too little share data. The tree includes loops and LIT directories, so traversal must avoid infinite recursion and count only distributed objects where appropriate. Operation polling and large streamed outputs are asynchronous and can expose timing or buffering issues.

## Test signals
Signals include mutable repair success after corrupt/deleted shares, exact deep-stats counts and histograms, stream-manifest counts and cap classifications, JSON health fields and share maps, deep-check and deep-check-and-repair aggregate counters, cancellation failure with `OperationCancelledError`, CLI manifest raw/storage-index/verify-cap/repair-cap variants, damaged-tree classifications, unrecoverable deep-check failure on a broken subdirectory, and streamed line counts for hundreds of LIT files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deepcheck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deferredutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deferredutil.py

## Purpose
This module tests Tahoe utility wrappers around Twisted Deferreds, including gathering behavior, delayed-call cleanup, retry-until loops, async coroutine adaptation, and a `race` helper that resolves on the first success or aggregates failures.

## Important APIs, types, and functions
- `DeferredUtilTests` covers `deferredutil.gatherResults`, `DeferredListShouldSucceed`, and `WaitForDelayedCallsMixin.wait_for_delayed_calls`.
- `UntilTests` covers `deferredutil.until`.
- `AsyncToDeferred` covers the `async_to_deferred` decorator.
- `_setupRaceState` builds cancellable Deferreds and cancellation counters.
- `RaceTests` covers `race` and `MultiFailure` using Hypothesis-generated before/after counts.

## Control flow
Gather/list tests create Deferreds manually, fire callbacks or errbacks in controlled order, and assert the aggregate result. `until` tests verify synchronous exceptions, repeated synchronous calls until a condition flips, and waiting for Deferred completion before the next iteration. `async_to_deferred` wraps async functions and inspects the resulting Deferred for success or captured exception. Race tests set up N Deferreds, trigger one success or all failures, and inspect the result Deferred plus cancellation side effects.

## State and persistence behavior
There is no filesystem persistence. State is held in Deferred callback chains, lists that record successes/failures/cancellation counts, and Twisted's reactor delayed-call queue. The delayed-call test specifically ensures pending calls are waited out so Trial does not report an unclean reactor.

## Dependencies and integration points
Dependencies include Twisted Trial, Twisted reactor and Deferred APIs, `twisted.python.failure.Failure`, Hypothesis integer strategies, and Tahoe `deferredutil`. The tests integrate Tahoe's Deferred helpers with Trial's synchronous and asynchronous result helpers.

## Risks
Cancellation semantics are subtle. `race` must cancel losers after a success, ignore later results from cancelled Deferreds without logged errors, tolerate cancellers that callback, and convert full failure or result cancellation into `MultiFailure`. `until` can spin if the action never returns a Deferred and condition never becomes true; the tests cover only bounded examples.

## Test signals
Signals include immediate errback propagation from gathered results, success-only list aggregation, failure wrapping as `Failure`, delayed-call drain behavior, `until` exception/result sequencing, coroutine success and exception adaptation, `race` winner index/result, loser cancellation counts, aggregate `MultiFailure.failures`, no logged errors for post-cancel results, and cancellation propagation to all inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_deferredutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dictutil.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dictutil.py

## Purpose
This module tests Tahoe dictionary utilities: a dictionary of sets, a dictionary with auxiliary serialized values, typed-key dictionaries for bytes/unicode separation, and a value-filter helper.

## Important APIs, types, and functions
- `dictutil.DictOfSets` is tested for `add`, duplicate handling, `discard`, automatic key removal when a set becomes empty, and `update` from another `DictOfSets`.
- `dictutil.AuxValueDict` is tested for `set_with_aux`, normal item assignment, aux lookup with defaults, deletion, constructors from mappings/iterables/kwargs, and aux reset after regular assignment.
- `dictutil.BytesKeyDict` and `UnicodeKeyDict` are tested for constructor and method-level type enforcement.
- `dictutil.filter` is tested for predicate-based value filtering.

## Control flow
The tests are straightforward synchronous Trial tests. They mutate utility dictionaries, compare keys and values after each operation, and assert `TypeError` or `KeyError` where appropriate. The typed-key tests exercise assignment, lookup, deletion, `setdefault`, and `get` with invalid key types, then repeat the same operations with valid key types.

## State and persistence behavior
All state is in memory. `DictOfSets` state is a mapping from key to `set`; the test confirms empty sets are not retained. `AuxValueDict` holds a main value map and separate auxiliary metadata map; the important behavior is that direct `__setitem__` clears auxiliary state for that key while `set_with_aux` sets both value and aux. Typed dictionaries preserve normal dict behavior for valid keys.

## Dependencies and integration points
Dependencies are limited to Twisted Trial and `allmydata.util.dictutil`. The utilities are likely used by directory metadata and other Tahoe internals where bytes/unicode distinction and auxiliary serialized forms matter.

## Risks
The main risk is silent type confusion between bytes and unicode keys, especially in Python 3 ported code. Another risk is stale auxiliary serialized data surviving after value replacement, which would desynchronize logical values from cached serialized forms. `DictOfSets.discard` must remain tolerant of missing keys.

## Test signals
Signals include duplicate add idempotence, missing discard no-op, key removal on empty set, update union semantics, aux defaults for missing keys, aux clearing on direct assignment, constructor parity for `AuxValueDict`, invalid-key `TypeError` for all public typed-dict methods, valid-key normal dict behavior, and exact filtered dictionary output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dictutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dirnode.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dirnode.py

## Purpose
This large module tests Tahoe-LAFS directory nodes across mutable SDMF/MDMF directories, immutable directory representations, child packing/unpacking, metadata/timestamp rules, Unicode normalization, unknown future caps, readonly behavior, deep-check/deep-stats integration, retry behavior after uncoordinated writes, overwrite rules, and deterministic directory capability generation from RSA keypairs.

## Important APIs, types, and functions
- `MemAccum` is an `IConsumer` test sink for reading tiny LIT directory children.
- `Dirnode` is the main grid-backed test case. Helpers `_do_create_test`, `_do_initial_children_test`, `_do_basic_test`, `_test_deepcheck_create`, `_do_readonly_test`, and `_do_create_subdirectory_test` drive most directory-node behavior for SDMF and MDMF variants.
- `Packing` tests `dirnode.pack_children`, `DirectoryNode._pack_contents`, `DirectoryNode._unpack_contents`, and deep-immutable enforcement.
- `FakeMutableFile`, `FakeNodeMaker`, and `FakeClient2` provide lightweight mutable-directory tests without a real grid for future/unknown caps.
- `Dirnode2` tests `UnknownNode`, `strip_prefix_for_ro`, and future cap preservation.
- `DeepStats` tests `dirnode.DeepStats`.
- `UCWEingMutableFileNode`, `UCWEingNodeMaker`, and `Deleter` test delete retry after `UncoordinatedWriteError`.
- `Adder` tests overwrite policy including `dirnode.ONLY_FILES`.
- `DeterministicDirnode` tests RSA-keypair-driven deterministic mutable directory caps.

## Control flow
Grid-backed tests create directories through a client `NodeMaker`, then chain Deferred callbacks that mutate children and verify every intermediate result. `_do_create_test` creates a mutable directory, adds mutable children, creates subdirectories, checks list/path lookup/metadata, tests `set_uri`, `set_node`, `set_children`, `set_nodes`, metadata updates, timestamp preservation on replacement, file upload, movement between directories, and `no-write` readonly attenuation. `_do_initial_children_test` creates directories with LIT, CHK, SSK, MDMF, unknown future caps, and LIT directories, then validates normalized child names and readable content. `test_immutable` builds immutable directories and rejects mutable or non-deep-immutable children. Deep-check helpers build a looped tree and assert object counters for healthy and missing-share cases. Tail tests cover packing round trips, future URI handling, stats histograms, retry after upload conflict, overwrite behavior, and deterministic cap derivation.

## State and persistence behavior
Directory state is persisted in mutable file contents encoded as netstrings of child name, read cap, encrypted write-cap data, and metadata. Tests inspect raw `download_best_version` bytes to ensure trailing spaces are preserved in storage while stripped during node creation/listing, and that names are stored/retrieved as Unicode NFC. Metadata state includes user keys plus Tahoe-managed `linkcrtime` and `linkmotime`; tests ensure callers cannot forge Tahoe timestamp fields, creation time is preserved on overwrite, and modification time increases. Share state is persisted in the no-network grid and can be damaged by deleting shares. Deterministic directory tests persist generated caps derived from RSA keypairs through mutable key derivation.

## Dependencies and integration points
The module integrates with Twisted Deferreds, Zope interfaces, Tahoe URI parsing, dirnode implementation, client/node maker APIs, RSA signing key generation and PEM loading, immutable upload/literal nodes, mutable file nodes and key derivation, mutable storage test utilities, no-network grid infrastructure, unknown-node handling, base32/hash helpers, netstring parsing, and Hypothesis. It is one of the core integration suites connecting directory semantics to mutable files, immutable files, cap handling, web-safe readonly attenuation, and deep traversal.

## Risks
The broadest risks are capability safety and data compatibility. Directory packing must preserve unknown future caps without accidentally granting write authority, enforce deep immutability for immutable directories, and keep bytes/unicode names normalized in a stable way across Unicode database changes. Metadata rules are security-sensitive because `no-write` attenuates mutable caps to readonly and Tahoe-managed timestamps must not be caller-controlled. Retry paths around `UncoordinatedWriteError` protect against misleading `NoSuchChildError`. The deterministic keypair tests mean key derivation or serialization changes can alter externally visible caps.

## Test signals
Signals include SDMF/MDMF cap prefixes and backing versions, empty and populated listing behavior, path lookups and missing-child errors, manifest/verifycap/storage-index sets, deep-stats counters and histograms, metadata/timestamp invariants, overwrite rejection and movement semantics, readonly node mutation failures, immutable directory LIT/CHK cap forms, future/unknown cap acceptance and rejection cases, pack/unpack byte-compatible known tree behavior, Hypothesis Unicode round trips, deep-check/deep-repair counters including loops and cache-miss ceiling, delete retry success after forced `UncoordinatedWriteError`, overwrite policy for files versus directories, and deterministic cap equality for known RSA keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_dirnode.py -->
