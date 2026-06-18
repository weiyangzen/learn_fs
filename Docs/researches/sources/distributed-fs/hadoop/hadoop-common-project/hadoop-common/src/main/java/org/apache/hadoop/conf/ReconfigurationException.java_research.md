# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationException.java`

## Purpose

`ReconfigurationException` signals that a runtime configuration change could not be applied. It carries the property name, requested new value, old value, and optionally a cause.

## Important APIs and Types

Constructors include a generic no-arg failure, a property/new/old constructor, and a property/new/old/cause constructor. Accessors are `getProperty`, `getNewValue`, and `getOldValue`.

## Control Flow

The property-specific constructors build a message with `constructMessage`, then store the three value fields. The class itself has no recovery behavior; callers catch it to report or store failure information.

## State and Persistence

The exception stores three mutable-looking private strings, though there are no setters. It is serializable through Java exception serialization with `serialVersionUID = 1L`.

## Dependencies and Integration Points

It is thrown by `Reconfigurable` implementations and caught by `ReconfigurableBase` and `ReconfigurationServlet`. Service code can wrap lower-level errors as the cause.

## Risks

The constructed message includes raw property values, which can expose secrets if a sensitive property is reconfigured and the message is logged or returned to a servlet client. Message formatting around missing old/new values is minimal and can produce less readable text.

## Test Signals

Tests should assert constructors populate fields, preserve causes, and generate expected messages for old-only, new-only, and both-value cases. Sensitive-value redaction should be tested at callers, because this exception does not redact.
