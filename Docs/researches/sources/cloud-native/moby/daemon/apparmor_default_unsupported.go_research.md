# sources/cloud-native/moby/daemon/apparmor_default_unsupported.go

## Purpose
Provides non-Linux fallback implementations for default AppArmor profile functions.

## APIs, Types, And Functions
The file defines `loadDefaultAppArmorProfileIfMissing`, `DefaultApparmorProfile`, and `installDefaultAppArmorProfile` for `!linux` builds.

## Control Flow, State, And Integration
All functions are no-ops or return an empty profile name. No profile state is loaded or persisted on unsupported platforms.

## Risks And Test Signals
Risks are low but important for cross-platform builds: callers must tolerate an empty default profile. Integration is with shared daemon code that references AppArmor helpers without platform conditionals.
