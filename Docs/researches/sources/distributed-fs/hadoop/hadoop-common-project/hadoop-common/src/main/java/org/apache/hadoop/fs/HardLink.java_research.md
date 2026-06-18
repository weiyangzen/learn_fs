# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HardLink.java

Purpose: `HardLink` provides static hard-link creation and link-count utilities with platform-specific fallback commands, plus per-instance counters for clients that track copy/link work.

Important APIs: constructor and `linkStats`, `createHardLink`, `createHardLinkMult`, `supportsHardLink`, `getLinkCount`, `LinkStats.clear`, and `LinkStats.report`.

Control flow and state: static initialization chooses a `HardLinkCommandGetter` based on platform and customizes the link-count command for macOS/FreeBSD/Solaris. Link creation uses Java NIO `Files.createLink`. Link-count retrieval first checks whether the file store supports the UNIX attribute view and reads `unix:nlink`; if not, it executes the platform command and parses output. `LinkStats` is mutable instance state and explicitly not thread-safe.

Dependencies and integration: used by local filesystem utilities and archive extraction hard-link handling. It depends on `Shell`, `ShellCommandExecutor`, Java NIO file attributes, `FileUtil.makeShellPath`, and `IOUtils`.

Risks: `supportsHardLink` only checks UNIX attribute view, so fallback commands handle other platforms but may depend on winutils or shell utilities. Solaris parses `ls -l` output differently. Static command selection is platform-global. Multi-link creation loops one NIO link per file rather than batching through a shell command.

Test signals: null/missing argument failures, single and multi-link creation, link count via NIO and command fallback, platform-specific command templates, winutils lookup on Windows, Solaris parsing, and `LinkStats` report formatting.
