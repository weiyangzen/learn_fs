# sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml lines 8053-16081

## Purpose

This chunk is part of Tahoe-LAFS' persisted integration-test capability vector corpus. The YAML records pre-generated upload inputs and the exact capability string expected after uploading those inputs through a Tahoe node. The consumer is `integration/test_vectors.py::test_capability`, which parametrizes over `integration.vectors.capabilities`, reconfigures Alice's node to the vector's ZFEC/convergence settings, uploads the generated sample bytes in the requested format, and asserts that the produced capability exactly matches the persisted `expected` value.

The selected line window is a large middle slice of the YAML vector list. It begins inside an MDMF RSA private-key scalar from the previous record and ends inside an SDMF RSA private-key scalar from the next record. Between those boundaries, the chunk contains 160 vector records that both start and finish inside the range, plus the closing part of the leading MDMF record and the opening part of the trailing SDMF record.

## Data Model And Fields

Each vector record uses the same schema loaded by `integration/vectors/vectors.py::load_capabilities`:

- `convergence`: base64-encoded 16-byte convergence secret, later decoded into `Case.convergence`.
- `expected`: Tahoe capability string. This chunk includes `URI:CHK`, `URI:SSK`, and `URI:MDMF` write capabilities.
- `format.kind`: either `chk` for immutable CHK uploads or `ssk` for mutable uploads.
- `format.params`: `null` for CHK, or an SSK parameter object with `format` set to `sdmf` or `mdmf`, a PEM RSA private `key`, and `mutable: null`.
- `sample.length` and `sample.seed`: compact plaintext description. The loader expands this with `stretch(seed, length)` rather than storing large test bodies directly.
- `zfec.required`, `zfec.total`, and `zfec.segmentSize`: encoding parameters used to reconfigure the node before upload.

The chunk exercises the fixed segment size `131072` throughout. The sampled object lengths appearing in this slice are `56`, `1024`, `4096`, `131071`, `131073`, `2097151`, `2097153`, `4194304`, `8388607`, and `8388609`, so it covers small non-LIT CHK input, one-segment boundary-adjacent inputs, and multi-segment Merkle-tree cases.

## Parameter Coverage

Within the selected lines there are 161 `- convergence:` starts, 54 `URI:CHK` expectations, 54 `URI:SSK` expectations, and 53 `URI:MDMF` expectations. Because the line window cuts through scalar blocks, these counts are best read as chunk-internal starts rather than whole-file totals.

The chunk covers both convergence secrets used by the generator:

- `YWFhYWFhYWFhYWFhYWFhYQ==`, the base64 form of `b"aaaaaaaaaaaaaaaa"`.
- `ZOyIygCyaOW6GjVnihtTFg==`, the first 16 bytes of `sha256(b"Hello world")`.

The ZFEC combinations in this slice include:

- `required: 2`, `total: 3`.
- `required: 3`, `total: 10`.
- `required: 71`, `total: 255`.
- `required: 101`, with CHK vectors materializing the symbolic max as `total: 256` and SDMF/MDMF vectors using `total: 255`.

That `255` versus `256` distinction is intentional. `integration/util.py::SSK.max_shares` caps SDMF/MDMF at 255 because those formats encode `N` and `k` directly into one byte, while `CHK.max_shares` is 256.

## Important APIs, Types, And Control Flow

The persisted YAML is interpreted by `integration/vectors/vectors.py`:

- `Case` holds `seed_params`, `convergence`, `seed_data`, `fmt`, and `segment_size`.
- `Sample` describes deterministic plaintext as repeated seed bytes plus a final length.
- `SeedParam.realize(max_total)` resolves symbolic maximum share counts per format.
- `load_format` maps `kind: chk` to `CHK.load` and `kind: ssk` to `SSK.load`.
- `load_capabilities` returns a `dict[Case, str]` from the YAML's `vector` list.

The test flow is:

1. `test_capability` receives one `Case` and expected capability from `vectors.capabilities.items()`.
2. `alice.reconfigure_zfec` writes `shares.happy`, `shares.needed`, `shares.total`, convergence secret, and `shares._max_immutable_segment_size_for_testing` as needed, restarting the node when configuration changes.
3. `upload(alice, case.fmt, case.data)` creates a temporary file from `Case.data`.
4. `CHK.to_argv()` contributes no extra CLI flags; `SSK.to_argv()` writes the persisted RSA private key to a temporary file and passes `--format=sdmf|mdmf --mutable --private-key-path=<temp>`.
5. `tahoe put` returns the capability string, which is compared byte-for-byte to `expected`.

The generator path, `skiptest_generate`, produced records from the Cartesian product of ZFEC parameters, convergence secrets, object descriptions, and formats. It uses `SSK.customize()` to generate RSA keys and `save_capabilities()` to persist the resulting YAML.

## State And Persistence Behavior

The YAML is durable golden-test state, not runtime application state. Its embedded RSA private keys are test fixtures required to make mutable SDMF/MDMF writecaps reproducible. CHK vectors are deterministic from plaintext, convergence secret, and encoding settings; SSK/MDMF vectors also depend on the stored private key.

At test runtime, the file is loaded once into `vectors.capabilities`. Each case mutates the Alice node configuration, possibly restarts the node, performs a single upload, and then discards temporary plaintext and temporary private-key files. The persisted vector file itself is only rewritten by the disabled generation helper.

## Dependencies And Integration Points

This chunk integrates with:

- PyYAML `safe_load` / `safe_dump` for vector serialization.
- `attrs` frozen classes for hashable `Case`, `Sample`, `Param`, and `SeedParam` values.
- Tahoe CLI behavior for `tahoe put`, including immutable CHK and mutable SDMF/MDMF upload paths.
- Tahoe client config keys for shares, convergence secret, and immutable segment size.
- Tahoe URI parsing/formatting in `src/allmydata/uri.py`, including `URI:CHK`, `URI:SSK`, and `URI:MDMF`.
- ZFEC encoding/decoding behavior via Tahoe's immutable and mutable upload implementations.
- RSA serialization support in the integration helper for generated mutable keys.

## Risks And Maintenance Notes

- The line range cuts through PEM scalar blocks. Chunk-level analysis should avoid treating the first and last records as independently valid YAML fragments.
- Any behavioral change in URI serialization, convergence hashing, segment sizing, mutable key handling, or ZFEC share-count semantics will intentionally break these golden vectors.
- The file stores many RSA private keys. They are test-only fixtures, but tooling should avoid logging or copying them unnecessarily.
- `CURRENT_VERSION` in `vectors.py` gates loading. If the YAML version changes without the loader version changing, the capability set becomes empty and the slow vector test would silently have no cases unless the test harness also guards for this.
- Large plaintexts are generated by repetition from small seeds. This gives deterministic coverage for segment-boundary behavior, but it is not high-entropy file-content coverage.
- The SSK max-share cap is format-specific. A mistaken normalization of `MAX_SHARES` to `256` for mutable vectors would create invalid or non-representable SDMF/MDMF cases.

## Test Signals

The main signal is `integration/test_vectors.py::test_capability`, marked slow. Passing this test means the current implementation can still regenerate every capability in the persisted corpus for the same inputs. This chunk specifically signals compatibility for mid-to-high ZFEC configurations (`2/3`, `3/10`, `71/255`, and `101/max`), both convergence secrets, all three upload formats, and object sizes around important segment boundaries.

Adjacent coverage in `integration/test_get_put.py::test_upload_download_immutable_different_default_max_segment_size` checks cross-version immutable segment-size download compatibility, while these vectors pin exact capability outputs for the older fixed `128 KiB` segment size used by the vector generator.
