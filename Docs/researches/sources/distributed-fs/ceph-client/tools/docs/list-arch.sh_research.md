<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/list-arch.sh -->
# sources/distributed-fs/ceph-client/tools/docs/list-arch.sh

Purpose: Small shell wrapper that prints feature support status for a requested architecture or the normalized host architecture.

Important APIs/types/functions: Exposes one optional positional argument, `ARCH`. It normalizes `uname -m` for x86 and s390 variants, then invokes `$(dirname $0)/get_feat.pl list --arch $ARCH`.

Control flow: Shell parameter expansion picks the supplied architecture or computes one from `uname -m`; execution is delegated entirely to `get_feat.pl`.

State and persistence: No state is stored. Output is whatever the feature-list command prints.

Dependencies/integration: Depends on `sed`, `uname`, and an adjacent `get_feat.pl` script. In this snapshot the Python replacement `get_feat.py` is present, so this wrapper is an integration compatibility point that may be stale if `get_feat.pl` is absent.

Risks/tests: The main risk is broken delegation to `get_feat.pl` when only `get_feat.py` exists. Test signals are running the wrapper with no args and with `x86`, `s390`, and another explicit architecture, verifying it matches `get_feat.py list --arch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/docs/list-arch.sh -->
