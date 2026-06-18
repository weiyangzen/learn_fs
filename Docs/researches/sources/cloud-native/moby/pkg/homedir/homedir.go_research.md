<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir.go -->
# sources/cloud-native/moby/pkg/homedir/homedir.go

Purpose: returns the current user's home directory in a cross-platform way. `Get` prefers environment variables appropriate for OS conventions and falls back to `os/user`. Control flow avoids expensive user lookup when `HOME` or Windows equivalents are present. State is only environment-derived. Dependencies are `os`, `os/user`, and `runtime`. Risks include empty or misleading environment variables, cross-compiled/runtime OS differences, and user lookup failure in minimal containers. Test signal is basic path non-empty/shape coverage in `homedir_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir.go -->
