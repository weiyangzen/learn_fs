# File Research: sources/block-storage/lvm2/libdm/libdevmapper.pc.in

Purpose: provides the pkg-config template for consumers linking against libdevmapper.

Read coverage: complete file read, 12 lines.

Key contents:
- Defines install-time variables `prefix`, `exec_prefix`, `libdir`, and `includedir`.
- Publishes package metadata: `Name: devmapper`, description `device-mapper library`, and version placeholder `@DM_LIB_PATCHLEVEL@`.
- Exposes compile flags as `-I${includedir}`.
- Exposes public linker flags as `-L${libdir} -ldevmapper`.
- Lists private dependencies for static/private linking through `Requires.private: @SELINUX_PC@ @UDEV_PC@`.
- Lists private libraries `-lm @RT_LIBS@ @PTHREAD_LIBS@`.

Dependencies:
- Filled by the build system from configure/meson-style substitution variables before installation.
- Represents SELinux, udev, realtime, pthread, and math dependencies without forcing all of them into dynamic consumers' public link lines.

Risk and edge cases:
- Incorrect substitution of private dependency placeholders can break static linking or overexpose platform libraries.
- The `Cflags` line has a trailing space after `${includedir}`, harmless for pkg-config but worth preserving only if generated output compatibility expects it.
