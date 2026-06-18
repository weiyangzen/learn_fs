## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs.go

Purpose: shared kernel knob model used by platform-specific OS tweak application.

Important APIs/types/functions: `conditionalCheck` function type; `OSValue` pairs a desired sysctl value with an optional predicate; `propertyIsValid` decides whether a new value should be applied.

Control flow: `propertyIsValid` returns true if no check function is supplied or if the predicate accepts the old and new values. Linux `ApplyOSTweaks` uses this before writing `/proc/sys`.

State and persistence behavior: no state. It is a pure helper around desired kernel configuration values.

Dependencies and integration points: used by `knobs_linux.go` and by `Namespace.ApplyOSTweaks` for ingress/load-balancer IPVS settings.

Risks: predicate semantics are broad; a misleading check function can prevent required sysctl updates or apply unsafe ones. There are no tests here for custom predicates.

Test signals: indirect only through Linux knob tests and any consumers that pass non-nil checks.
