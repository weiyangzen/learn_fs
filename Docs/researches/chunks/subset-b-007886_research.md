# sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml lines 1-8052

## Purpose

This chunk is the opening portion of Tahoe-LAFS's generated capability test-vector fixture. It is YAML data, not executable code, and it records precomputed upload capabilities for a matrix of deterministic inputs. Each vector describes the plaintext sample to synthesize, the convergence secret to configure, the object/capability format to upload, the ZFEC share parameters to use, and the exact URI capability expected from Tahoe-LAFS.

The surrounding integration suite uses this file to lock Tahoe-LAFS capability generation against known-good outputs. `integration/vectors/vectors.py` loads the full file from `DATA_PATH`, validates the persisted `version`, converts rows into hashable `Case` objects, and exposes `capabilities`. `integration/test_vectors.py` parametrizes `test_capability` over that dictionary, reconfigures an `alice` node with each case's convergence and ZFEC parameters, uploads deterministic data, and asserts the resulting capability string equals the `expected` URI.

Lines 1-8052 contain 162 vector entries and stop in the middle of the 162nd entry's PEM-encoded RSA private key. The full YAML document continues after this chunk and only declares `version: 2023-01-16.2` at the end of the file, so this chunk by itself is intentionally not a standalone YAML document.

## Data Contract and Important Types

Each list item under top-level `vector:` follows the schema consumed by `load_capabilities`:

- `convergence`: base64-encoded 16-byte convergence secret. This chunk uses `YWFhYWFhYWFhYWFhYWFhYQ==` for `b"aaaaaaaaaaaaaaaa"` and `ZOyIygCyaOW6GjVnihtTFg==` for the first 16 bytes of `sha256(b"Hello world")`.
- `expected`: exact capability URI produced by Tahoe-LAFS for the case. CHK entries use `URI:CHK:<storage-index>:<verify-cap>:<required>:<total>:<size>`. Mutable entries use `URI:SSK:...` for SDMF and `URI:MDMF:...` for MDMF.
- `format.kind`: either `chk` or `ssk`. CHK rows have `params: null`; SSK rows carry mutable parameters.
- `format.params.format`: `sdmf` or `mdmf` for mutable cases.
- `format.params.key`: a PEM `RSA PRIVATE KEY` captured during vector generation so mutable cap generation is repeatable.
- `format.params.mutable`: `null` in this chunk.
- `sample.length` and `sample.seed`: instructions for building test plaintext via `stretch(seed, length)`, which repeats the decoded seed and truncates to the desired byte length.
- `zfec.required`, `zfec.total`, and `zfec.segmentSize`: share reconstruction threshold, total shares, and segment size used when reconfiguring the test node.

The Python-side types represented by these YAML fields are `Case`, `Sample`, `SeedParam`, and `Param` from `integration/vectors/vectors.py` and `integration/vectors/model.py`. `Case.data` materializes plaintext from `Sample`; `Case.params` realizes `SeedParam` against the format's maximum share count; `load_format` maps `kind: chk` to `CHK.load(...)` and `kind: ssk` to `SSK.load(...)`.

## Chunk Coverage

Within lines 1-8052, the matrix is highly regular:

- 162 vector starts and 162 `expected` values are visible.
- 54 rows are `chk`; 108 rows are `ssk`.
- Mutable rows split evenly between `sdmf` and `mdmf` in the visible complete field counts: 54 each.
- 120 visible completed ZFEC parameter blocks use `required: 1`; 41 use `required: 2`. The final visible MDMF row begins before its trailing sample/ZFEC block appears, so one `required: 2,total: 3,segmentSize: 131072` block is in the next chunk.
- 60 visible completed ZFEC parameter blocks use `total: 1`; 101 use `total: 3`.
- All visible completed ZFEC blocks use `segmentSize: 131072`, matching `parameters.SEGMENT_SIZE`.
- The first convergence secret accounts for 90 vector starts in this chunk; the second accounts for 72.

The tested sample lengths visible here are `56`, `1024`, `4096`, `131071`, `131073`, `2097151`, `2097153`, `4194304`, `8388607`, and `8388609`. These correspond to the generator's object descriptions around small non-LIT data, one-segment boundaries (`128 KiB - 1` and `+ 1`), and larger segment-multiple boundaries.

## Control Flow and Integration

The data lifecycle starts in `skiptest_generate` in `integration/test_vectors.py`. That helper constructs the Cartesian product of:

- `parameters.ZFEC_PARAMS`
- `parameters.CONVERGENCE_SECRETS`
- `parameters.OBJECT_DESCRIPTIONS`
- `parameters.FORMATS`

For each case, the generator reconfigures the Tahoe node, customizes mutable formats so they have concrete RSA keys, uploads deterministic data, and calls `save_capabilities`. `save_capabilities` serializes the same fields visible here: convergence, format description, sample descriptor, ZFEC parameters, and expected cap.

At test time, `vectors.py` calls `safe_load` on the full file, checks `data["version"] == CURRENT_VERSION`, decodes base64 bytes, constructs `SeedParam`, `Sample`, and loaded `CHK`/`SSK` format objects, then returns a dictionary keyed by `Case`. `test_capability` replays each case by calling `alice.reconfigure_zfec(..., (1, required, total), convergence, segment_size)`, uploads `case.data` in `case.fmt`, and compares the resulting cap to the stored `expected`.

This YAML file therefore sits at the integration boundary between the Python test harness, Tahoe node configuration, mutable key handling, CHK/SSK/MDMF URI generation, convergent encryption, and ZFEC encoding.

## State and Persistence Behavior

The file is a persistent golden dataset. It has no runtime state of its own, but it persists state that would otherwise be nondeterministic or expensive to regenerate:

- The expected capability URIs encode Tahoe-LAFS's historical output for specific parameter combinations.
- Mutable `ssk` entries persist per-case RSA private keys. Without these PEM keys, SDMF and MDMF capabilities would change when regenerated.
- The convergence secrets and sample seeds are base64 text so binary values survive YAML serialization.
- The top-level version field, outside this chunk at the end of the full file, gates loader compatibility. If the version differs from `CURRENT_VERSION`, `load_capabilities` returns no cases.

Because `safe_load` is applied to the whole file, the end-of-file `version` field and all continuation lines after 8052 are required for normal operation. A chunked research reader must not treat lines 1-8052 as parseable YAML.

## Dependencies

The visible data depends on the schema and behavior of:

- `yaml.safe_load` and `yaml.safe_dump` for round-tripping simple YAML values.
- Base64 helpers `encode_bytes` and `decode_bytes` for convergence secrets and sample seeds.
- Tahoe integration format helpers `CHK` and `SSK`, including `CHK.load`, `SSK.load`, `SSK.customize`, and each format's URI-generation behavior during upload.
- `stretch(seed, size)`, which deterministically expands each sample seed into test plaintext.
- `parameters.SEGMENT_SIZE`, fixed at `128 * 1024`.
- Tahoe node reconfiguration through `Client.reconfigure_zfec`, including happy/required/total share settings and convergence secret propagation.
- The upload helper in `integration.util`, which uploads the generated plaintext and returns a capability string.

## Risks and Edge Cases

- The YAML file stores real-looking RSA private keys for deterministic test vectors. They are test fixtures, but tooling should still avoid leaking them into logs unnecessarily or treating them as production secrets.
- The full file places `version` after the large `vector` list. Loaders that stream only the beginning, or chunk consumers that parse partial content, cannot validate compatibility.
- Lines 1-8052 end mid-PEM. Any line-based chunk merge must preserve exact ordering and indentation; otherwise the full YAML scalar for the final visible key will be corrupted.
- Capability strings are exact golden values. Intentional changes to URI encoding, convergence hashing, segment splitting, mutable-key handling, or ZFEC parameter realization will cause broad test failures and require regenerating vectors with a deliberate version bump.
- The vectors include sizes just below and above segment boundaries. These are sensitive to off-by-one errors in segment layout, Merkle tree construction, and CHK URI size fields.
- CHK and mutable formats have different maximum-share semantics in the model. Later full-file chunks cover `MAX_SHARES` cases; this first chunk already exercises `total: 1` and `total: 3`.
- Because `load_capabilities` returns a dictionary keyed by `Case`, duplicate logical cases later in the file would silently overwrite earlier expected strings. The regular product structure makes duplicates unlikely, but generator or serialization changes should keep this in mind.

## Test Signals

Strong test signals from this chunk include:

- Loading the full fixture should produce `Case` instances whose sample data lengths match the listed `sample.length` values and whose decoded convergence secrets are exactly 16 bytes.
- For each complete row in this chunk, upload output should equal the stored `expected` URI for the matching format, sample, convergence, segment size, and ZFEC tuple.
- CHK cases should have `format.params: null` and expected URIs ending with the original plaintext length.
- SDMF and MDMF cases should use persisted PEM keys and produce `URI:SSK:` and `URI:MDMF:` prefixes respectively.
- Boundary sizes `131071`, `131073`, `2097151`, `2097153`, `8388607`, and `8388609` should be preserved exactly; replacing them with rounded segment sizes would invalidate the vectors.
- Re-running `skiptest_generate` without intentional fixture refresh should not be part of normal CI, because these tests are meant to compare against the originally captured outputs rather than moving outputs.

## Chunk Boundary Notes

This chunk begins at the start of the file and captures the `vector:` key and many complete vector entries. It ends at line 8052 inside the RSA private key scalar for a `URI:MDMF:qxw7uvec...` vector with convergence `ZOyIygCyaOW6GjVnihtTFg==`, sample length `131071`, and ZFEC settings that start in the immediately preceding complete CHK/SSK rows. The continuation of that PEM key, its `mutable`, `sample`, and `zfec` fields, plus the remaining matrix rows and final `version` field, are outside this work item and must be handled by later chunks before producing the final per-file research document.
