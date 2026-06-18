# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/Makefile.am

Purpose: this Automake file builds `libgfchangelog.la`, the changelog client/library target used by examples and internal consumers such as bitrot.

Important declarations: it sets `AUTOMAKE_OPTIONS = subdir-objects`, declares `lib_LTLIBRARIES = libgfchangelog.la`, and lists sources including `gf-changelog.c`, journal handler, helpers, API, history support, RPC/reborp code, and changelog RPC common code from the xlator source tree. Headers are listed in `noinst_HEADERS`. It links against libglusterfs, XDR, and RPC libraries.

Control flow and state: no runtime control flow, but compile flags define `DATADIR`, file offset support, PIC, and include paths required by RPC, xlator, and changelog internals. The `version-info` setting controls the library ABI version.

Dependencies and integration points: this is the build bridge between changelog xlator internals and the standalone `libgfchangelog` API. It depends on generated XDR headers, rpc-lib, socket transport headers, and libglusterfs. It also includes a make rule to build `libglusterfs.la`.

Risks: missing generated XDR include paths or source-list drift can break library builds. ABI-sensitive changes need matching `LIBGFCHANGELOG_LT_VERSION` management. Since the library includes source from `xlators/features/changelog/src`, build ordering must remain correct.

Test signals: recursive make should produce `libgfchangelog.la`; pkg-config users should compile the C examples; symbol checks should show live, generic, and history changelog APIs.
