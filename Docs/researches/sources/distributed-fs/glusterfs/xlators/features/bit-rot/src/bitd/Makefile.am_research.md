<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/Makefile.am

## Purpose
Build recipe for the daemon-side bit-rot translator module.

## APIs, Types, and Functions
When `WITH_SERVER` is enabled, builds `bit-rot.la` from `bit-rot.c`, `bit-rot-scrub.c`, `bit-rot-ssm.c`, and `bit-rot-scrub-status.c`. Private headers include `bit-rot.h`, scrub headers, message IDs, and state-machine header. It links libglusterfs and `libgfchangelog.la`, and compiles with `-DBR_RATE_LIMIT_SIGNER`.

## Control Flow, State, and Persistence
Automake sets include paths for libglusterfs, RPC/XDR, rpc-lib, timer-wheel contrib code, and the bit-rot stub. Runtime behavior is in the C sources.

## Dependencies and Integration
Depends on server builds, changelog library, timer-wheel, bit-rot stub headers, and GlusterFS core headers. Installs as an xlator under `features`.

## Risks and Test Signals
Risks include server-disabled omission, link dependency drift with changelog/timer-wheel, and CFLAGS changing signer throttling behavior. Test signals are server build/link, module load, changelog integration, and scrub/signing runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/Makefile.am -->
