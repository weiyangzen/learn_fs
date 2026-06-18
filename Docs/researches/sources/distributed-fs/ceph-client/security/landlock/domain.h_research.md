# sources/distributed-fs/ceph-client/security/landlock/domain.h

## Purpose

`domain.h` defines Landlock domain hierarchy metadata, audit log state, domain-origin details, and hierarchy reference helpers.

## Important APIs, Types, and Functions

`enum landlock_log_status` tracks pending, recorded, or disabled domain logging. `struct landlock_details` stores creator PID, UID, command, and executable path. `struct landlock_hierarchy` links a domain to its parent and stores reference count plus audit fields such as ID, denial count, details, and logging flags. `landlock_get_hierarchy()` increments references, and `landlock_put_hierarchy()` walks up parents freeing nodes whose usage drops to zero. Audit stubs are provided when `CONFIG_AUDIT=n`.

## Control Flow

Ruleset creation allocates a hierarchy node; inheritance pins the parent hierarchy; ruleset freeing calls `landlock_put_hierarchy()`, which may log domain deallocation, free details, move to the parent, and continue until a referenced ancestor is reached.

## State and Persistence Behavior

Hierarchy nodes outlive individual ruleset pointers as long as child domains or credentials reference them. Audit details are immutable after creation. Parent references preserve domain ancestry for ptrace/scope checks and audit attribution.

## Dependencies and Integration Points

The header integrates with ruleset lifetime, audit logging, ID generation, and task/scope checks outside this work item.

## Risks and Test Signals

Reference-count mistakes can drop parent hierarchy too early or leak ancestry. The free loop must call audit drop before freeing details. Test nested restrict-self calls, parent process exit before child, audit deallocation records, and scope comparisons.
