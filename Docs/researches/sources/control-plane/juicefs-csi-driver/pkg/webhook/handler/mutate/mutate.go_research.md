<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/mutate.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/mutate.go

### Purpose
`mutate.go` defines the minimal interface contract for admission pod mutators in the JuiceFS webhook package.

### Important APIs, Types, And Functions
`Mutate` is an interface with `Mutate(ctx context.Context, pod *corev1.Pod) (*corev1.Pod, error)`.

### Control Flow
There is no implementation flow in this file. Concrete mutators, especially `SidecarMutate`, satisfy this interface and can be used through interface-typed constructors.

### State, Persistence, And Dependencies
No state is stored. Dependencies are `context` and Kubernetes `corev1.Pod`.

### Integration Points
`handler.go` creates a mutator through `mutate.NewSidecarMutate` and invokes it through this interface, keeping the admission handler decoupled from concrete mutation internals.

### Risks
The interface is intentionally broad and does not specify whether implementations mutate the input pod or return a deep copy. Callers should treat the returned pod as authoritative.

### Test Signals
Useful signals are compile-time interface assertions in concrete mutators and handler tests that exercise behavior through the interface rather than concrete-only methods.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/mutate.go -->
