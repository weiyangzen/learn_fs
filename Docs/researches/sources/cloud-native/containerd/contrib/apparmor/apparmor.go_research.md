<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor.go -->
# sources/cloud-native/containerd/contrib/apparmor/apparmor.go

## Purpose
Linux AppArmor OCI spec integration for applying existing or generated default profiles.

## Important APIs, Types, And Functions
Provides `WithProfile` and `WithDefaultProfile` spec opts on supported builds.

## Control Flow
Spec opts ensure Linux config exists, optionally generate/load default profile, and set `s.Process.ApparmorProfile`.

## State And Persistence
May load AppArmor policy into kernel via parser and reads/writes profile data through template helpers.

## Dependencies And Integration Points
OCI spec opts, AppArmor parser/template helpers, Linux/AppArmor availability.

## Risks And Test Signals
Requires AppArmor and parser on host; profile load failures affect container creation. Tests/fuzzer cover default profile generation. Source size reviewed: 95 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/apparmor/apparmor.go -->
