<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_linux.go -->
# sources/cloud-native/containerd/pkg/rdt/rdt_linux.go

## Purpose
Linux RDT integration layer that configures Intel resctrl/goresctrl support and maps Kubernetes/container annotations to RDT classes.

## Important APIs, Types, And Functions
IsEnabled reads guarded package state. SetConfig initializes goresctrl once, loads a config file with SetConfigFromFile, and marks RDT enabled. ContainerClassFromAnnotations delegates class selection to goresctrl.

## Control Flow
SetConfig disables RDT first, exits quietly for empty config, performs one-time rdt.Initialize, returns cached initialization errors, applies config, then sets enabled true.

## State And Persistence
Maintains process-global enabled state with RWMutex plus initOnce/initErr for one-time resctrl initialization. External persistence is the kernel resctrl filesystem state written by goresctrl.

## Dependencies And Integration Points
Depends on github.com/intel/goresctrl/pkg/rdt and containerd log. Called from CRI/runtime configuration paths when RDT is enabled.

## Risks And Edge Cases
Initialization is one-shot: a failed first Initialize is cached. Config changes affect global RDT state. Linux-only build excludes no_rdt.

## Test Signals
No direct tests in subset; behavior depends on goresctrl and host resctrl support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_linux.go -->
