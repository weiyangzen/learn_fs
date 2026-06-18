## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystem.java

Purpose: Public abstract service API for registering sources, sinks, callbacks, and controlling metrics publication.

Important APIs/types/functions: Defines `init`, `start`, `stop`, `shutdown`, source/sink `register`, `unregisterSource`, `publishMetricsNow`, JMX MBean start/stop, `currentConfig`, `getSource`, and `Callback` lifecycle hooks with `AbstractCallback` no-op base.

Control flow: Concrete implementation orchestrates configuration load, timer scheduling, callback invocation, sampling, and sink publication.

State and persistence: Abstract only, but contract implies global service lifecycle and restart behavior.

Dependencies/integration: `DefaultMetricsSystem` exposes a singleton; components register metrics through this API.

Risks/test signals: Callback exceptions should not break service lifecycle in `MetricsSystemImpl`. Tests should cover duplicate registration, source unregistering, shutdown reference counting, and immediate publish.
