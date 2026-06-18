# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/SignalUtil.java

## Purpose
`SignalUtil` wraps non-public JDK signal APIs through Hadoop dynamic binding utilities so the rest of Hadoop can handle and raise signals without direct compile-time dependency on `sun.misc.Signal`.

## Important APIs, Types, And Functions
Important pieces are dynamic bindings for `sun.misc.Signal`, `sun.misc.SignalHandler`, constructor, static `handle`, static `raise`, handler `handle`, nested `Signal`, nested `Handler`, and `JdkSignalHandlerImpl`.

## Control Flow
Static initializers load classes and bind constructors/methods. `Signal(String)` creates a JDK signal delegate and binds get-number/name calls. `Signal(Object)` validates delegate type. `JdkSignalHandlerImpl(Handler)` creates a dynamic proxy implementing JDK `SignalHandler`; proxy `handle` calls the Hadoop handler with a wrapped signal and delegates other methods reflectively. `handle` installs a proxy and returns the previous handler wrapped. `raise` invokes the JDK raise method.

## State And Persistence
State is dynamic method metadata and wrapper delegates. Installing handlers mutates process-level signal handler state.

## Dependencies And Integration Points
It depends on Hadoop `BindingUtils`, `DynConstructors`, `DynMethods`, `Preconditions`, Java reflection/proxy APIs, and the JDK's internal signal classes when present. `SignalLogger` is its main local consumer.

## Risks
Non-public JDK APIs can be inaccessible under module restrictions or alternate JVMs. Static dynamic binding failures may surface at class initialization or first use. Proxy fallback for non-handle methods assumes the user handler has matching methods.

## Test Signals
Tests should cover signal name construction, delegate wrapping validation, equality/hash/toString, handler install returning previous handler, proxy invocation, raise behavior, and unavailable-class failure modes.
