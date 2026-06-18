## sources/distributed-fs/openafs/src/rxkad/Makefile.in

### Purpose
`rxkad/Makefile.in` builds the traditional rxkad security library, generated error/header files, installable public headers, and test utility targets.

### Important APIs, Types, And Functions
Primary targets are `all`, `generated`, `depinstall`, static `librxkad.a`, shared `liboafs_rxkad.la`, PIC `librxkad_pic.la`, `tcrypt`, `install`, `dest`, and `clean`. Generated files come from `rxkad_errs.et` through `COMPILE_ET_C` and `COMPILE_ET_H`.

### Control Flow
The build links rxkad client/server/common, fcrypt, packet crypt, ticket, ticket5, CRC, and generated error objects against comerr, rx, opr, and RFC3961/hcrypto libraries. Dependency rules install public headers into `TOP_INCDIR`.

### State, Persistence, And Dependencies
Persistent outputs include libraries, generated `rxkad_errs.c`, generated `rxkad.h`, installed `fcrypt.h`, `rxkad_prototypes.h`, `rxkad_convert.h`, and stats header. `clean` also recurses into `test`.

### Integration Points
This is the build bridge between legacy rxkad code, Heimdal-derived ticket/DER support, and the OpenAFS Rx library. `ticket5.lo` includes generated/rewritten v5 sources and suppresses deprecated declaration warnings.

### Risks
The makefile mixes generated headers with source headers, so dependency order matters. `crypt_conn.c` and `bg-fcrypt.c` provide overlapping packet crypto implementations depending on build context. Install target omits some depinstalled headers such as stats/convert compared with `depinstall`.

### Test Signals
Clean rebuilds, generated header regeneration, static/shared/PIC library link checks, `tcrypt` build/run, install/dest staging, and test-directory clean behavior are useful signals.
