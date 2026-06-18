# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/PowerShellFencer.java

Purpose: Windows-oriented fencing method that generates and runs a temporary PowerShell script to terminate remote `java.exe` processes whose WMI `CommandLine` contains a configured process-name fragment.

Important APIs and types: `PowerShellFencer extends Configured implements FenceMethod`, with `checkArgs()`, `tryFence()`, and private `buildPSScript()`.

Control flow: `tryFence()` takes the configured process-name argument and target hostname, builds a `.ps1` script containing a `Get-WmiObject Win32_Process -Filter ... -Computer host |% { $_.Terminate() }` command, starts `powershell.exe` with the script path, pumps stdout/stderr with `StreamPumper`, waits for process exit, and returns success for exit code 0.

State and persistence: Creates a temporary script file marked `deleteOnExit()`. It persists no Java-side state, but can kill remote processes as its external side effect.

Dependencies and integration points: Invoked through `NodeFencer` alias `powershell`. Depends on Windows PowerShell, WMI permissions, target address metadata, and `StreamPumper`.

Risks: `checkArgs()` logs but does not validate null/empty process names. Process-name text is embedded into a WMI filter without escaping, so malformed input can break the script. `deleteOnExit()` is delayed until JVM exit. Success only reflects PowerShell exit status, not necessarily that the intended process died.

Test signals: Windows-specific or mocked process tests should verify script construction, process-name filtering, error output pumping, exit-code handling, and behavior for missing PowerShell or bad arguments.
