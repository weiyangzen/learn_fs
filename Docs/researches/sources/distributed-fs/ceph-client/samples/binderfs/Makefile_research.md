# sources/distributed-fs/ceph-client/samples/binderfs/Makefile

Purpose: registers the Android binderfs userspace example for kbuild.

Important APIs/types/functions: `userprogs-always-y += binderfs_example` and `userccflags += -I usr/include`.

Control flow: kbuild builds `binderfs_example` whenever the binderfs sample directory is selected.

State and persistence: no runtime state; produces a userspace binary.

Dependencies and integration: selected by `CONFIG_SAMPLE_ANDROID_BINDERFS`; includes installed UAPI headers through `usr/include`.

Risks: missing headers_install output breaks compilation. The sample itself requires mount namespace and binderfs privileges at runtime.

Test signals: enable `SAMPLE_ANDROID_BINDERFS`, build samples, and verify include path resolves binder headers.
