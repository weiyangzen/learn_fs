<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Kconfig -->
# sources/distributed-fs/ceph-client/fs/vboxsf/Kconfig

Purpose: Declares the kernel configuration option for the VirtualBox guest shared folder filesystem.

Important APIs, types, and functions: Defines `CONFIG_VBOXSF_FS` as a tristate option named "VirtualBox guest shared folder (vboxsf) support". It depends on `(ARM64 || X86) && VBOXGUEST` and selects `NLS`.

Control flow: The Kconfig entry controls whether the vboxsf module is built in, built as a module, or omitted. Selecting it makes the Kbuild rules in the same directory build the vboxsf object set.

State and persistence: No runtime state. The selected config determines availability of the `vboxsf` filesystem type and whether NLS conversion support is linked.

Dependencies and integration points: Integrates with the VirtualBox guest driver (`VBOXGUEST`), architecture support limited to ARM64 and X86, and kernel NLS facilities used by mount option parsing and filename conversion.

Risks and test signals: Risks are build exposure on unsupported architectures or without the VirtualBox guest device. Test all three tristate modes, X86 and ARM64 configs, dependency exclusion, and module autoload by filesystem alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/vboxsf/Kconfig -->
