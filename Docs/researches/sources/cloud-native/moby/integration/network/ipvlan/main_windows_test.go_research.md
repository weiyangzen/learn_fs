<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/ipvlan/main_windows_test.go

Purpose: Windows package stub for `integration/network/ipvlan`.

Important APIs/types/functions: declares `package ipvlan` only; there are no tests, setup functions, or exported helpers.

Control flow: none.

State/persistence: none.

Dependencies/integration: exists so the package has a Windows build target despite the real ipvlan tests being behind `!windows` build tags.

Risks: no Windows coverage for ipvlan behavior; this is expected because ipvlan is not exercised by this package on Windows.

Test signals: compile-only signal that the package is valid on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_windows_test.go -->
