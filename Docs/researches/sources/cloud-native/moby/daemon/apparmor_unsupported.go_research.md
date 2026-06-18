# sources/cloud-native/moby/daemon/apparmor_unsupported.go

## Purpose
Provides unsupported-platform fallback for AppArmor support detection.

## APIs, Types, And Functions
The file defines `appArmorSupported` for non-AppArmor build targets, returning false.

## Control Flow, State, And Integration
There is no runtime probing. Shared daemon code can call the function safely and receive an unsupported result.

## Risks And Test Signals
Risk is limited to ensuring build tags select the correct implementation. Integration is with cross-platform daemon security configuration.
