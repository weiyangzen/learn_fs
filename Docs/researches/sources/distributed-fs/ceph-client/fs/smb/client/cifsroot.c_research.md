# sources/distributed-fs/ceph-client/fs/smb/client/cifsroot.c

Purpose: implements early-boot CIFS root filesystem parameter handling for `cifsroot=`, allowing the kernel to mount an SMB share as the root filesystem.

Important APIs and functions: defines default root mount options in `DEFAULT_MNT_OPTS`, stores early root device/options in `root_dev` and `root_opts`, parses IPv4 server addresses with `parse_srvaddr`, handles the boot parameter in `cifs_root_setup`, registers it via `__setup("cifsroot=", ...)`, and exposes `cifs_root_data` to return the parsed device and options to root-mount code.

Control flow: `cifs_root_setup` runs during early parameter parsing. If the argument looks like `//server/share[,options]`, it sets `ROOT_DEV = Root_CIFS`, copies the UNC path up to the comma into `root_dev`, extracts an IPv4 address from the server portion into `root_server_addr`, and appends user-supplied options to the default mount option string. Later, `cifs_root_data` verifies that a device and server address were recorded and returns pointers to the static buffers.

State and persistence behavior: state is early-init static data marked `__initdata`; it persists only during boot setup. The effective root mount options default to SMB1-era settings including `vers=1.0`, `cifsacl`, `mfsymlinks`, large `rsize`, fixed `wsize`, uid/gid 0, hard mount, and `rootfs`, with user options appended.

Dependencies and integration points: depends on Linux init parameter parsing, root device selection, `root_server_addr` from IP autoconfiguration/root infrastructure, IPv4 `in_aton`, and CIFS mount option parsing later in the normal SMB client mount stack. It is invoked before the full filesystem module mount flow.

Risks: IPv6 is explicitly unsupported. Address parsing accepts only digits and dots from the server substring, so DNS names or bracketed IPv6 cannot populate `root_server_addr`. The default `vers=1.0` is insecure and may conflict with modern servers or with configurations that disable legacy dialects. Option string length is bounded and truncation returns an early error. `cifs_root_setup` returns `1` even on ignored or failed parse paths, following `__setup` convention but requiring log messages for diagnosis.

Test signals: boot parameter tests for valid `//IPv4/share`, option append, too-long UNC, too-long options, missing share, DNS name, invalid address, absent `cifsroot`, and root mount handoff; modern SMB server tests requiring `vers=3.x` override; and explicit coverage that IPv6 remains rejected or is implemented intentionally.
