# sources/cloud-native/containers-storage/pkg/regexp/regexp_dontprecompile.go

Purpose: default build configuration for lazy regex compilation.

Important APIs, types, and functions: constant `precompile = false`.

Control flow: no runtime flow; `regexp.go` reads this constant in `Delayed` and `compile`.

State and persistence: no state. It changes whether regex state is created at declaration or first use.

Dependencies and integration points: selected when build tag `regexp_precompile` is absent. It is the normal startup-optimized path.

Risks and edge cases: invalid regex patterns panic later at first method call, which can defer failures into runtime paths.

Test signals: normal tests run under this behavior unless the build tag is set.
