# sources/distributed-fs/ceph-client/tools/net/ynl/ynltool/Makefile

Purpose: builds and installs the C `ynltool` utility from all `*.c` files in the directory.

Important build variables: includes `../Makefile.deps`, uses `gcc`, `-Wall -Wextra -Werror -O2`, optional sanitizer/debug flags under `DEBUG=1`, include paths for YNL lib/generated headers and UAPI, and `SRC_VERSION` derived from the kernel Makefile. `OBJS` honors `OUTPUT`, and `YNLTOOL` is `$(OUTPUT)ynltool`.

Control flow: `all` builds `ynltool`. The link rule depends on `../libynl.a` and object files, linking with `-lm`. Pattern rule compiles with dependency output. The lib rule delegates to the parent YNL Makefile. `install` copies the binary to `$(DESTDIR)$(bindir)/$(YNLTOOL)`.

Dependencies/integration: compiles `main.c`, `page-pool.c`, `qstats.c`, and `json_writer.c` against generated `netdev-user.h` and YNL runtime.

Risks/test signals: `-Werror` makes compiler-version warnings fatal. The install destination appends `$(YNLTOOL)`, so non-empty `OUTPUT` can affect the installed filename if not normalized by callers. Successful `make` and `ynltool version` are basic signals.
