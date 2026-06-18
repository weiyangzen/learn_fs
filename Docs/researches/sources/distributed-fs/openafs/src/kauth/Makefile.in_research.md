# sources/distributed-fs/openafs/src/kauth/Makefile.in

Purpose: Automake-style makefile template for building OpenAFS kauth libraries, generated RPC sources, server/client tools, tests, install targets, and cleanup rules.

Important targets and variables: object groups `BASE_objs`, `LT_objs`, `LWP_objs`, `KRB_objs`; dependency/library groups `LT_deps`, `LIBS`, `KLIBS`; `all`, `depinstall`, `generated`, `liboafs_kauth.la`, `libkauth_pic.la`, `libkauth.a`, `libkauth.krb.a`, `kaserver`, `kas`, `klog`, `klog.krb`, `knfs`, `kpasswd`, `kpwvalid`, `kdb`, `ka-forwarder`, `rebuild`, `install`, `dest`, and `clean`.

Control flow and state: generated files come from `kauth.rg` through `RXGEN` and from `kaerrors.et` through `COMPILE_ET`. Many object targets depend on generated `kautils.h`. Install/dest actions are gated by `INSTALL_KAUTH`.

Dependencies and integration: ties kauth to ubik, auth, prot, sys, rxkad, rx, lwp, cmd, com_err, audit, afsutil, opr, hcrypto/rfc3961, and roken. The researched `admin_tools.c`, `authclient.c`, and `client.c` build into libraries and commands here.

Risks: generated-header dependencies are critical for parallel builds; missed dependencies can race. The `clean` target removes generated RPC/error outputs and programs. Test signals are `make generated`, `make depinstall`, full `make`, `make test`, and install/dest dry runs with both `INSTALL_KAUTH` settings.
