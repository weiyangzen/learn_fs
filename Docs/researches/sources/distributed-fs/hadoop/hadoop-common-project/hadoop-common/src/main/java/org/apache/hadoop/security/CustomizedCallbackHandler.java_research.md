# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/CustomizedCallbackHandler.java


Purpose: `CustomizedCallbackHandler` is an extension point for SASL callback customization beyond Hadoop's built-in callback handling.

Important APIs and types: It is an interface with `handleCallbacks(List<Callback>, String, char[])`. Nested `Cache` memoizes configured handlers by configuration key. `DefaultHandler` rejects any non-empty callback list. `delegate(Object)` adapts legacy objects with a compatible `handleCallbacks` method through reflection.

Control flow and state: `Cache.get()` checks a static map, instantiates the class configured under a key, falls back to `DefaultHandler` on construction failure, wraps non-interface objects through reflection, and caches successful custom handlers. `clear()` resets the static cache for tests.

Dependencies and integration: It depends on Hadoop `Configuration`, JAAS callbacks, reflection, and SLF4J. It is intended to be called by SASL client/server paths after standard name/password handling to process custom callbacks.

Risks and test signals: Static caching means configuration changes may not take effect until `clear()`. Reflection-based delegates can fail at runtime if signatures drift. Tests should cover interface implementations, delegate objects, default rejection, construction failure fallback, and cache clearing.
