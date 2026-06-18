# sources/cloud-native/cri-o/internal/version/linkmode_static.go

Purpose: supplies the link mode value for static builds.

Important APIs/types/functions: declares `const linkmode = "static"` under build constraint `static`.

Control flow: compile-time selection when the `static` build tag is present.

State and persistence: contributes to version info output only.

Dependencies/integration: paired with `linkmode_dynamic.go` and read by `Get` in `version.go`.

Risks: mismatched build tags would make static builds report incorrectly or fail compilation.

Test signals: best verified by compiling with `-tags static` and checking `Get(false).Linkmode`.
