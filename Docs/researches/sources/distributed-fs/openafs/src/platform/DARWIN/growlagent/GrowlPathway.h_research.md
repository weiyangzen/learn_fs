# Research: sources/distributed-fs/openafs/src/platform/DARWIN/growlagent/GrowlPathway.h

Purpose: declares the Growl pathway protocol and base class used for in-process or distributed Growl notification handling.

Important APIs and state: `GrowlNotificationProtocol` declares one-way `registerApplicationWithDictionary:` and `postNotificationWithDictionary:` plus `growlVersion`. `GrowlPathway` subclasses `NSObject` and conforms to the protocol without declaring ivars.

Control flow and persistence: header-only contract. Implementations receive registration dictionaries and notification dictionaries, then return version information.

Dependencies and integration: imports Foundation and references `GrowlApplicationController`. Used by Growl agent components under the Darwin platform tree.

Risks: the protocol uses Distributed Objects-style `oneway` and `bycopy` annotations, which are legacy and constrain object serialization to property-list-like dictionaries. The header alone does not validate required Growl keys.

Test signals: protocol conformance in implementation classes, distributed object invocation, dictionary copy semantics, registration followed by notification, and version string compatibility with Growl clients.
