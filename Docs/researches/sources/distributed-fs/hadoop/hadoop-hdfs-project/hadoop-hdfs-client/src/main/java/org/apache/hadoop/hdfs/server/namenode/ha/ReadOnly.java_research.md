# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/ReadOnly.java

Purpose: `ReadOnly` is a runtime-retained method annotation used by HDFS HA client code to identify RPCs that can be routed to Observer NameNodes.

Important APIs/types/functions: annotation attributes are `atimeAffected`, `activeOnly`, and `isCoordinated`, all defaulting to false. `activeOnly=true` excludes an otherwise read-like method from observer routing. `isCoordinated=true` indicates server-side processing should wait for state alignment if behind the client.

Control flow: `ObserverReadProxyProvider` and `RouterObserverReadProxyProvider` inspect the annotation at invocation time. Server-side RPC handling can also inspect coordination metadata.

State and persistence behavior: annotation metadata is retained at runtime and inherited; there is no mutable state.

Dependencies and integration points: integrates with HDFS `ClientProtocol` method declarations, observer-read clients, and state-alignment logic.

Risks and test signals: incorrect annotation can route a mutating or active-only operation to observers, or unnecessarily force active routing. Tests should verify representative annotated methods are classified as expected and that `activeOnly` prevents observer use.
