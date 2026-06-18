# sources/distributed-fs/ceph-client/tools/net/ynl/Makefile

Purpose: Top-level build, install, test, lint, and cleanup coordinator for the YNL tooling tree.

Important targets and variables: Includes `../../scripts/Makefile.arch` to derive `LP64`, selects `lib` versus `lib64`, and defines `prefix`, `libdir`, `includedir`, and `SPECDIR`. `SUBDIRS` covers `lib`, `generated`, `ynltool`, and `tests`. `all` builds subdirectories and `libynl.a`; `libynl.a` archives `lib/ynl.o` plus generated user objects.

Control flow: Subdirectory targets recurse only when a local Makefile exists. `tests`, `ynltool`, and `libynl.a` use order-only prerequisites to ensure library and generated code are built first. `install` installs the static archive, public headers under `include/ynl`, the Python package via `pip install --prefix`, and generated/ynltool assets. `schema_check` iterates every YAML netlink spec and validates it through `pyynl/cli.py`.

Dependencies and integration: Integrates the C library, generated protocol bindings, Python `pyynl` package, `ynltool`, test suite, `yamllint`, and documentation netlink specs under `Documentation/netlink/specs`.

State and persistence: Produces local archives, object files, generated artifacts, Python build metadata/cache directories, and installed files under `DESTDIR`.

Risks: `pip install --prefix=$(DESTDIR)$(prefix) .` can interact poorly with distribution packaging or virtualenv policy. The archive depends on generated `*-user.o` files being present. `schema_check` continues through all specs but only reports TAP-like output, so callers must inspect failures unless make exit behavior is added.

Test signals: Run `make`, `make run_tests`, `make schema_check`, `make lint`, `make clean`, `make distclean`, and staged `make DESTDIR=... install` on both LP64 and non-LP64 configurations.
