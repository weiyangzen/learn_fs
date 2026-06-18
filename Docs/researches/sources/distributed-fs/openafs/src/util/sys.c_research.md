# sources/distributed-fs/openafs/src/util/sys.c

Purpose: Tiny utility program that prints the configured OpenAFS `SYS_NAME`.

Important API/function: `main()` prints `SYS_NAME` followed by a newline and exits successfully.

Control flow and state: No persistent state; includes generated `AFS_component_version_number.c` for version metadata side effects used by the build.

Dependencies and integration: Includes OpenAFS config headers and stdio. Built as a utility to expose platform/system naming.

Risks and test signals: Behavior depends entirely on the configured `SYS_NAME` macro. Tests are simple execution output checks after configure/build.
