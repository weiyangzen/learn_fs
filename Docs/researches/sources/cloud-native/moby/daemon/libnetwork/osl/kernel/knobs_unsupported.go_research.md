## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_unsupported.go

Purpose: non-Linux no-op implementation of OS tweak application.

Important APIs/types/functions: build-tagged `ApplyOSTweaks(osConfig map[string]*OSValue)` that does nothing.

Control flow: no-op for all input.

State and persistence behavior: no state and no system mutation.

Dependencies and integration points: keeps callers portable when Linux `/proc/sys` is unavailable.

Risks: platform behavior diverges; callers expecting network sysctls to be applied must not assume this works outside Linux.

Test signals: build coverage only.
