# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleTcpClientHandler.java

Purpose: default Netty handler for `SimpleTcpClient`, responsible for sending the XDR request on connection.

Important APIs/types/functions: constructor, `channelActive`, `channelRead`, and `exceptionCaught`.

Control flow: on active connection it writes the request using TCP record-mark framing. Default `channelRead` closes after any response, allowing subclasses to parse before close. Exceptions log a warning and close the channel.

State and persistence: stores the request; no persistence.

Dependencies and integration: used by `SimpleTcpClient`; subclassed by `RegistrationClientHandler`.

Risks: log message has a typo (`PRC`). `exceptionCaught` logs `cause.getCause()`, which can hide the actual exception when cause has no nested cause. Default handler discards response content.

Test signals: covered by simple TCP and registration client tests.
