<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/validator.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/validator.go

### Purpose
`validator.go` defines the generic validator interface used by webhook validation components.

### Important APIs, Types, And Functions
`Validator[T any]` declares `Validate(ctx context.Context, obj T) error`.

### Control Flow
There is no executable control flow beyond the interface declaration.

### State, Persistence, And Dependencies
No state is stored. The only dependency is `context`.

### Integration Points
`SecretValidator` asserts it implements `Validator[corev1.Secret]`. Additional validators can share the same typed interface.

### Risks
The interface does not distinguish transient from permanent errors or expose admission warning messages, so callers map all errors to a single admission failure path.

### Test Signals
Compile-time interface assertions in concrete validators are the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/validator.go -->
