## sources/distributed-fs/ipfs-kubo/test/sharness/t0295-multibase.sh

Purpose: validates `ipfs multibase` list, encode, decode, and transcode CLI behavior for stdin and file inputs, including failure messages for invalid prefixes/characters.

Important commands and control flow: creates expected encoded values, checks `multibase list`, encodes stdin and files with default/custom bases, decodes stdin and files, performs encode/decode roundtrips, transcodes between bases, and asserts errors on unknown prefixes and invalid characters.

State and persistence: no daemon or repo state is needed; temporary input and output files capture command results for `test_cmp`.

Dependencies and integration points: depends on multibase registry, CLI input dispatch, base-specific validators, and sharness comparison helpers.

Risks and test signals: good coverage for streaming/file input parity and error semantics. It is sensitive to list ordering and registry additions if expected fixtures are exact.
