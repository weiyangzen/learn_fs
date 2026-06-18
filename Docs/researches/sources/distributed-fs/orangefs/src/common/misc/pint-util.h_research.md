# sources/distributed-fs/orangefs/src/common/misc/pint-util.h

Purpose: Declares common internal utility contracts and portability macros for OrangeFS code that needs attribute conversion, timing, filesystem statistics, UID/GID access, digests, and alias generation.

Important APIs and types: `PINT_CONVERT_ATTR` maps `PVFS_sys_attr` common fields into `PVFS_object_attr` masks. `PINT_time_marker` holds wall, user, and system `timeval` samples. Prototypes cover tag allocation, object-attribute copy/free, time helpers, UID/GID wrappers, `PINT_util_bytes2str`, digest lifecycle/SHA1/MD5 helpers, and `PINT_util_guess_alias`. The header also abstracts `statfs`/`fstatfs` as `PINT_statfs_*` macros or Windows declarations.

Control flow: Header-only control flow is macro expansion. `PINT_CONVERT_ATTR` resets the destination mask, copies only source-mask-selected fields, preserves explicit atime/mtime set bits, and ORs caller-provided extra mask bits. Platform `statfs` macros choose Linux `sys/vfs.h`, BSD-style `sys/mount.h`, or the Windows shim implemented in `pint-util.c`.

State and persistence: No state is defined here. State belongs to implementations or callers. Macro use mutates caller-provided structures directly.

Dependencies and integration points: Pulls in `pvfs2-internal.h`, `pvfs2-types.h`, and `pvfs2-attr.h`; many client/server modules include this to avoid platform-specific filesystem-stat and attr-mask conditionals.

Risks: `PINT_CONVERT_ATTR` is a multi-statement macro that evaluates `dest` and `src` repeatedly and should only be used with stable lvalues. The digest functions are declared here but implemented elsewhere, so link coverage is needed. The header emits compile-time errors on platforms lacking supported `statfs` headers unless the Windows path is selected.

Test signals: Compile on all supported platform macro combinations, verify attr-mask conversions for every common field and explicit time-set bit, and ensure Windows callers see the same `PINT_statfs_*` accessor contract as POSIX callers.
