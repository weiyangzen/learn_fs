<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/overlay/main_windows_test.go

Purpose: Windows package stub for `integration/network/overlay`.

Important APIs/types/functions: contains only `package overlay`.

Control flow: none.

State/persistence: none.

Dependencies/integration: keeps the overlay package buildable on Windows while the real tests are behind `!windows`.

Risks: no Windows overlay behavior is covered in this package.

Test signals: compile-only Windows package signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_windows_test.go -->
