# sources/cloud-native/cri-o/internal/signals/signal.go

Purpose: exposes cross-platform signal aliases.

Important APIs/types/functions: package variables `Interrupt` and `Kill`.

Control flow: no functions; aliases are initialized from `os.Interrupt` and `os.Kill`.

State and persistence behavior: process-local variables only.

Dependencies and integration points: used by code that wants a CRI-O-local signals package while sharing names across platforms.

Risks: variables rather than constants can be reassigned inside the package. Signal semantics still depend on OS behavior.

Test signals: compile-time coverage only in this subset.
