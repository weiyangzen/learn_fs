<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template.go -->
# sources/cloud-native/containerd/contrib/apparmor/template.go

## Purpose
Generates, loads, and checks containerd AppArmor profile templates.

## Important APIs, Types, And Functions
Defines `defaultTemplate`, `data`, `cleanProfileName`, `loadData`, `generate`, `load`, `macroExists`, `aaParser`, and `isLoaded`.

## Control Flow
Builds template data from profile name and AppArmor macro availability, renders a profile, invokes apparmor parser for loading, and checks loaded profiles.

## State And Persistence
Reads `/etc/apparmor.d`, invokes system parser, and affects kernel AppArmor profile state.

## Dependencies And Integration Points
text/template, os/exec, AppArmor filesystem/proc interfaces.

## Risks And Test Signals
Shelling out to parser and host-specific macros make behavior environment-dependent. Tests cover name cleaning/template basics. Source size reviewed: 205 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/template.go -->
