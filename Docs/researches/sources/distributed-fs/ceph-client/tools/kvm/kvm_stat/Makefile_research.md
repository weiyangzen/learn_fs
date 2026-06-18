<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/Makefile -->
# sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/Makefile

Purpose: this Makefile builds and installs the `kvm_stat` man page and installs the Python tool into a target bindir.

Important APIs/targets: it includes shared tool makefiles, sets `BINDIR`, `MANDIR`, `MAN1DIR`, `MAN1`, and `A2X`, resolves `a2x` with `get-executable`, and defines targets `all`, `clean`, `man`, `install-man`, `install-tools`, and `install`.

Control flow: default `all` depends on `man`. The `%.1: %.txt` rule errors if `a2x` is missing, otherwise runs `a2x --doctype manpage --format manpage`. Install targets create destination directories and copy `kvm_stat.1` and `kvm_stat` with install modes.

State and persistence: generated state is `kvm_stat.1`; installed state goes under `$(INSTALL_ROOT)/usr/bin` and `$(INSTALL_ROOT)/usr/share/man/man1`.

Dependencies/integration: depends on asciidoc/a2x and kernel tools makefile helpers. The `install-tools` target honors `TARGET` for destination filename.

Risks and test signals: risk is missing `a2x`, incorrect install root, or stale man page. Test `make man`, `make clean`, and staged `make INSTALL_ROOT=/tmp/... install`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/Makefile -->
