<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/macvlan/main_windows_test.go

Purpose: Windows package stub for `integration/network/macvlan`.

Important APIs/types/functions: contains only `package macvlan`.

Control flow: none.

State/persistence: none.

Dependencies/integration: keeps the package buildable on Windows while real macvlan tests are Linux-only.

Risks: there is no Windows functional coverage in this package; that matches driver/platform availability expectations.

Test signals: compile-only Windows package presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_windows_test.go -->
