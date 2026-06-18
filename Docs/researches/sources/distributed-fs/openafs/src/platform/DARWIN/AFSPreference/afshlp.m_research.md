# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/afshlp.m

Purpose: tiny setuid-style exec helper.

Important APIs and control flow: `main` reads the effective uid, calls `setuid(euid)`, and then `execve(argv[1], &argv[1], envp)`. It returns `-1` if `setuid` fails.

State and persistence: no persistent state. It transforms process credentials and executes the requested program.

Dependencies and integration: used by `AFSCommanderPref krb5KredentialAtLoginTimeEvent:` as the helper path passed to `PListManager krb5TiketAtLoginTime:helper:`, though the visible plist manager implementation does not use that argument.

Risks: no argument-count check before `argv[1]`. If installed setuid, it is a broad exec primitive for any supplied path and arguments. Error reporting from `execve` failure is absent.

Test signals: invocation with no argv[1], valid target execution, environment preservation, setuid failure, and installed permissions.
