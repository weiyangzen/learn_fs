# sources/control-plane/rook/pkg/operator/ceph/predicate.go

Purpose: provides a typed controller-runtime predicate for filtering operator-settings ConfigMap events.

Important APIs/types/functions: `operatorSettingConfigMapPredicate[T *corev1.ConfigMap]()` returns `predicate.TypedFuncs[T]` with Create, Delete, Update, and Generic filters.

Control flow: Create and Generic events are ignored. Delete events are accepted only when the deleted ConfigMap name is `rook-ceph-operator-config`. Update events are accepted only when the new object has that name. This limits watches to changes relevant to operator config settings.

State and persistence behavior: no writes or persistence. It only examines event objects.

Dependencies/integration: depends on controller-runtime typed event/predicate APIs and `corev1.ConfigMap`. It integrates with controllers that watch the operator config map and need to ignore unrelated ConfigMap churn.

Risks: the function is unexported and generic, so usage depends on same-package integration. Updates are keyed only by name, not namespace; callers must scope watches appropriately. Creates are ignored, meaning a newly created settings ConfigMap will not trigger through this predicate unless another path loads it.

Test signals: no direct test file in this subset; behavior is simple but create-ignore semantics should be covered where used by controllers.
