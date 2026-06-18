<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-boot.am -->
## sources/cloud-native/ostree/Makefile-boot.am

### Purpose
This fragment installs boot integration assets: dracut modules, mkinitcpio hooks, systemd units, tmpfiles rules, and GRUB generator scripts.

### APIs, Types, and Control Flow
Conditional blocks add dracut module/config files, mkinitcpio install/config files, and systemd unit data depending on `BUILDOPT_*` flags. If built-in grub2 mkconfig is disabled, it installs `grub2-15_ostree` as a package libexec script and creates a symlink in `$(sysconfdir)/grub.d` through an install hook; otherwise it installs the internal `ostree-grub-generator` under the OSTree boot script directory.

### State, Dependencies, and Integration
Install-time state is written under `/lib/dracut`, `/lib/initcpio`, `/etc`, `/lib/systemd/system`, `/lib/tmpfiles.d`, and `/etc/grub.d` depending on prefix/sysconfdir. It integrates with `INSTALL_DATA_HOOKS` from `Makefile-decls.am` and top-level dist packaging.

### Risks and Test Signals
Boot path conventions vary by distro, and the fragment intentionally avoids `$(libdir)` for dracut modules. Symlink creation must respect `DESTDIR`. Test signals include `make install`, distcheck configure flags, bootc tests, and boot/admin integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-boot.am -->
