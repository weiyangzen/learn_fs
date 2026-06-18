# sources/distributed-fs/ceph-client/fs/nls/Kconfig

## Purpose
This Kconfig file defines the kernel Native Language Support configuration menu. It enables the base NLS layer and exposes individual codepage/charset modules used by filesystems such as FAT, Joliet, HFS/HFS+, SMB/NCP, and related legacy filename encodings.

## Important APIs, Types, And Functions
The top-level `menuconfig NLS` is a tristate that builds `nls_base` when enabled. `NLS_DEFAULT` selects the default mount-time charset string. Individual `config NLS_CODEPAGE_*`, `NLS_ISO8859_*`, `NLS_KOI8_*`, `NLS_MAC_*`, `NLS_UTF8`, and hidden `NLS_UCS2_UTILS` symbols drive Makefile object inclusion.

## Control Flow
There is no runtime control flow. Configuration flow is conditional: all child options are visible only inside `if NLS`. User choices become `CONFIG_NLS_*` symbols consumed by the NLS Makefile and by filesystem code that requests charset tables.

## State, Persistence, And Dependencies
The persistent state is the generated kernel `.config`. Many entries are tristate so encodings can be built in, built as loadable modules, or disabled. The help text documents intended filesystem usage and the valid strings for `NLS_DEFAULT`.

## Integration Points
`fs/nls/Makefile` maps these symbols to object files. Filesystems use NLS by calling the core NLS lookup/register APIs and by accepting mount options such as `iocharset=` or defaults from `CONFIG_NLS_DEFAULT`.

## Risks
The default string is free-form and can name a charset that was not built; the help text says the kernel falls back to a built-in iso8859-1-compatible table. Some help text is historical and broad, so distro configs may enable many rarely-used modules. Adding a new charset requires keeping Kconfig, Makefile, module name, and userspace mount strings consistent.

## Test Signals
Useful checks are `olddefconfig/menuconfig` visibility, build matrices for built-in and module NLS options, module autoload by charset name, and filesystem mount tests using explicit and default charset options.
