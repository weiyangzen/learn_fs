# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acdispat.h

Purpose: declares the ACPICA dispatcher layer that bridges parsed AML operations to namespace loading and interpreter execution.

Important APIs/functions: declarations cover dynamic argument evaluation, control-op begin/end, late operand evaluation, method execution callbacks, field creation, namespace load pass callbacks, method local/argument management, control method call/restart/termination, object and package initialization, operand/result-stack utilities, scope-stack manipulation, walk-state lifecycle, and method-stack debug dumps.

Control flow: table loading uses pass 1 and pass 2 dispatcher callbacks to build namespace state. Runtime method execution creates walk states, parses AML, manages scope/operand/result stacks, resolves operands, dispatches opcodes, handles predicates/control flow, calls nested methods, and terminates methods while releasing state.

State and persistence: state lives in walk states, thread state, parse objects, namespace nodes, operand objects, result stacks, method locals/args, and method descriptors. This header owns no storage.

Dependencies and integration: depends on `aclocal.h`, `acobject.h`, parser structures, and namespace nodes. It integrates parser (`ps*`), namespace (`ns*`), and executor (`ex*`) objects.

Risks: stack ownership, implicit return handling, result deletion, method serialization/restart, mutex release, and namespace mutation are subtle. Load-pass mistakes can create missing or duplicate namespace objects.

Test signals: AML load passes, nested scopes, control flow, implicit returns, field/bank/index/buffer field creation, package init, nested methods, method errors, and operand stack underflow/overflow.
