# sources/distributed-fs/tahoe-lafs/integration/vectors/test_vectors.yaml lines 16082-18002

## Scope

This chunk covers the tail of Tahoe-LAFS capability test vector data in `integration/vectors/test_vectors.yaml`. The assigned line range begins in the middle of the PEM private key for the SDMF case that starts at line 16064, then continues through the final complete vector records and the top-level `version: 2023-01-16.2` field at line 18002. Because this is YAML data rather than executable code, the important API surface is the persisted schema consumed by `integration/vectors/vectors.py` and exercised by `integration/test_vectors.py`.

## Purpose

The file is a persisted compatibility oracle for Tahoe-LAFS capability generation. Each vector describes:

- a 16-byte convergence secret encoded with base64;
- a target object format, either immutable CHK or mutable SSK with `format: sdmf` or `format: mdmf`;
- deterministic sample plaintext instructions, made from a base64 seed repeated/truncated to `sample.length`;
- ZFEC parameters, including `required`, `total`, and `segmentSize`;
- the expected read/write capability URI produced by `tahoe put`.

This chunk specifically covers high-share-count cases where `required` is `101` and `total` is the maximum supported by each format: `256` for CHK and `255` for SDMF/MDMF. It also covers the second configured convergence secret (`ZOyIygCyaOW6GjVnihtTFg==`, the first 16 bytes of `sha256(b"Hello world")`) across the whole object-size sample set.

## Schema And Important Data Shapes

Visible records use the same repeated YAML item structure:

- `convergence`: base64 text decoded to bytes by `decode_bytes`.
- `expected`: a Tahoe capability URI. CHK records include URI fields for storage index, verify cap hash, required shares, total shares, and size. Mutable records use `URI:SSK:` for SDMF and `URI:MDMF:` for MDMF.
- `format.kind`: `chk` or `ssk`.
- `format.params`: `null` for CHK; for SSK, a mapping with `format` (`sdmf` or `mdmf`), `mutable: null`, and a PEM RSA private `key`.
- `sample.seed` and `sample.length`: input to `stretch(seed, length)`, so large plaintexts are generated without storing large byte arrays in the YAML.
- `zfec.required`, `zfec.segmentSize`, and `zfec.total`: used to reconfigure the Tahoe node before upload.

The chunk contains 37 top-level vector starts in-range, plus the trailing fields of the SDMF record that began just before the chunk. The complete in-range record starts are:

- First convergence secret `YWFhYWFhYWFhYWFhYWFhYQ==` (`b"aaaaaaaaaaaaaaaa"`): MDMF for 4 MiB, then CHK/SDMF/MDMF triples for `8388607` and `8388609` bytes.
- Second convergence secret `ZOyIygCyaOW6GjVnihtTFg==`: CHK/SDMF/MDMF triples for `56`, `1024`, `4096`, `131071`, `131073`, `2097151`, `2097153`, `4194304`, `8388607`, and `8388609` bytes.

The sample lengths intentionally sit around thresholds: smallest non-LIT CHK input (`56`), small single-segment inputs, one byte below and above the 128 KiB segment size, one byte below and above 16 segments, exactly 32 segments, and one byte below and above 64 segments. This range helps detect off-by-one behavior in segment splitting, Merkle tree construction, and capability derivation.

## Consumer APIs And Types

`integration/vectors/vectors.py` is the direct reader/writer:

- `DATA_PATH` points to this YAML file.
- `CURRENT_VERSION` must match the file's `version`; otherwise `load_capabilities` prints a version mismatch and returns no cases.
- `Case` is an attrs-frozen key type containing `seed_params`, `convergence`, `seed_data`, `fmt`, and `segment_size`.
- `Case.data` calls `stretch(seed, length)` to materialize the plaintext.
- `Case.params` realizes symbolic max-share parameters against the selected format's `max_shares`.
- `load_format` maps `format.kind` to `CHK.load` or `SSK.load`.
- `load_capabilities` converts each YAML record into a `dict[Case, str]` mapping case inputs to expected capability URI.
- `save_capabilities` is the inverse used by the disabled generator path and emits this schema with ASCII-safe YAML.

Supporting model objects in `integration/vectors/model.py` include `Sample`, `Param`, and `SeedParam`. `SeedParam.realize(max_total)` is important for these records because the source parameter set uses a symbolic max-share intent, while the persisted YAML has already resolved it to `256` for CHK and `255` for mutable formats.

Format integration lives in `integration/util.py`:

- `CHK.kind == "chk"` and `CHK.max_shares == 256`; it contributes no extra CLI arguments.
- `SSK.kind == "ssk"` and `SSK.max_shares == 255`; `SSK.to_argv` writes the persisted PEM key to a temporary file and invokes `tahoe put --format=<sdmf|mdmf> --mutable --private-key-path=<temp>`.
- `upload` writes materialized case data to a temporary file, invokes the Tahoe CLI, and returns the stripped capability string.
- `reconfigure` rewrites `shares.needed`, `shares.total`, the private convergence secret, and the test-only immutable segment-size config before restarting the node when necessary.

## Control Flow

The runtime verification path is:

1. Importing `integration.vectors` opens `test_vectors.yaml` and calls `load_capabilities`.
2. `yaml.safe_load` parses the whole document into a mapping with `version` and `vector`.
3. Each record is decoded into a `Case`; base64 fields become bytes, CHK/SSK format objects are reconstructed, and SSK private keys remain attached to their case format.
4. `integration/test_vectors.py::test_capability` parametrizes over `vectors.capabilities.items()`.
5. The `alice` Tahoe node is reconfigured to `(happy=1, required=case.params.required, total=case.params.total)`, the vector convergence secret, and the 128 KiB segment size.
6. The deterministic plaintext is uploaded in the requested format.
7. The resulting capability is compared exactly with the YAML `expected` URI.

The generation path is intentionally disabled as `skiptest_generate`. When manually renamed/enabled, it iterates the Cartesian product from `parameters.py`, customizes mutable formats with fresh RSA keys, uploads through Tahoe, and repeatedly rewrites the accumulated YAML via `save_capabilities`.

## State And Persistence Behavior

This chunk is pure persisted test data. It stores deterministic inputs and expected outputs, but no runtime state. The only mutable behavior is external: the generator may overwrite the whole YAML file, and the test path reconfigures a temporary Tahoe client node. SSK/MDMF vectors persist RSA private keys so mutable capability generation is reproducible; losing or changing any key changes the expected mutable capability.

The final `version: 2023-01-16.2` anchors compatibility with `CURRENT_VERSION`. If a future generator changes capability semantics or schema, the version must change in lockstep with loader support or tests will silently skip all loaded vectors by returning `{}` after a mismatch.

## Dependencies And Integration Points

Key dependencies are:

- PyYAML `safe_load`/`safe_dump` for schema parsing and serialization.
- `attrs.frozen` for hashable immutable case objects.
- base64 for ASCII-safe byte fields.
- Twisted `FilePath` for locating the YAML next to the loader.
- Tahoe-LAFS CLI behavior for `tahoe put`, mutable format selection, and returned capability strings.
- Tahoe node configuration for convergence secret, ZFEC share parameters, and `_max_immutable_segment_size_for_testing`.
- RSA key serialization for SDMF/MDMF vectors.

The most important code integration points are `integration/test_vectors.py`, `integration/vectors/vectors.py`, `integration/vectors/parameters.py`, and `integration/util.py`. NEWS notes that these vectors are intended for compatibility verification between Tahoe-LAFS and other implementations, so external implementations may also treat this YAML as an interoperability contract.

## Risks And Edge Cases

- The assigned chunk begins inside a literal PEM block. Chunk-level readers must avoid treating line 16082 as a record boundary; the SDMF vector starts at line 16064.
- SSK and MDMF records contain large PEM private-key scalars. Naive text scans for strings like `URI:` or YAML-looking keys inside scalar bodies can miscount records; top-level indentation or a YAML parser is safer.
- CHK and mutable formats have different maximum share counts. These records depend on `total: 256` for CHK and `total: 255` for SDMF/MDMF; normalizing them would break the vectors.
- Expected capability URIs are exact golden values. Any change in convergence hashing, segment sizing, ZFEC parameter handling, mutable key handling, URI encoding, or Tahoe CLI output formatting can fail the tests.
- The `56` byte case is just above the literal-file cutoff described in `parameters.py`; changing the LIT threshold or immutable upload selection may alter CHK expectations.
- Boundary sizes around `131072`, `2097152`, and `8388608` are deliberate. Off-by-one changes in segment count, padding, or Merkle tree layout are likely to surface here.
- The loader returns an empty capability set on version mismatch after printing a message. That can make `test_capability` collect no parametrized cases instead of producing direct per-vector failures.
- The embedded RSA private keys are test fixtures, not secrets for production use, but accidental replacement or reformatting changes mutable capabilities.

## Test Signals

Primary signal: `integration/test_vectors.py::test_capability` should pass for every loaded case. For this chunk, meaningful coverage includes:

- exact capability equality for CHK, SDMF, and MDMF;
- correct reconstruction of sample data using repeated seeds for lengths from `56` through `8388609`;
- correct reconfiguration of `required=101`, `total=255/256`, convergence secret, and `segmentSize=131072`;
- stable handling of the final `version` field;
- YAML loader tolerance for long PEM scalar values.

If a regression affects only mutable formats, expect failures in the SDMF/MDMF cases while paired CHK cases for the same convergence/length still pass. If a regression affects segmentation or share encoding, failures should cluster around `131071`, `131073`, `2097151`, `2097153`, `8388607`, and `8388609`.
