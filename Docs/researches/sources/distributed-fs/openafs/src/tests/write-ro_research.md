# sources/distributed-fs/openafs/src/tests/write-ro

Purpose: shell regression check that writes to a replicated read-only volume fail. It attempts to create `../../replicated/foo`.

Important APIs and control flow: the script runs `touch ../../replicated/foo || exit 0` and then `exit 1`. Success is inverted: if `touch` fails, the script exits zero; if `touch` succeeds, it exits one.

State and persistence: on a broken environment where the write succeeds, it leaves `foo` in the replicated tree before failing. There is no cleanup because the success case is considered a failure. Dependencies are `/bin/sh`, `touch`, and the test harness layout where `../../replicated` points at a read-only AFS replicated volume.

Risks/test signals: the test only distinguishes touch success from failure and does not inspect errno, ACLs, or volume type. If the path is missing for reasons unrelated to read-only enforcement, the script still passes. Its signal is therefore suitable only in a carefully prepared AFS test cell.
