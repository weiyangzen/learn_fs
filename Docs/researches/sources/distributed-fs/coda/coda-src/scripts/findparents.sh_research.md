# sources/distributed-fs/coda/coda-src/scripts/findparents.sh

Purpose: quick diagnostic script to find backup volumes in `VolumeList` that appear to lack parent entries.

Control flow: prints a heading, extracts the eighth field for lines containing `backup`, strips leading `W`, loops each id, tests whether `/vice/vol/VolumeList` contains `I<id>`, and for missing parents prints selected information from matching `W<id>` lines.

State/persistence: read-only against `VolumeList`; no writes.

Dependencies, risks, tests: depends on current directory `VolumeList` for the first grep and absolute `/vice/vol/VolumeList` for subsequent checks, plus fixed field layout from Coda volume lists. Risks include inconsistent relative/absolute inputs, broad `grep backup` matching, and fragile text parsing. Test with known backup/parent pairs, missing parents, unusual names containing `backup`, and running outside `/vice/vol`.
