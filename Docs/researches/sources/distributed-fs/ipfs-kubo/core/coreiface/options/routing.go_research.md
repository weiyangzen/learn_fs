# sources/distributed-fs/ipfs-kubo/core/coreiface/options/routing.go

## Purpose
Builds settings for routing put/provide/find-provider operations.

## Important APIs, Types, and Functions
Defines `RoutingPutSettings`, `RoutingProvideSettings`, `RoutingFindProvidersSettings`, option types, builder functions, deprecated `Put` alias, `Routing` namespace, and methods `Recursive`, `NumProviders`, and `AllowOffline`.

## Control Flow and State
Routing put defaults to disallow offline writes, provide defaults to non-recursive, and find-providers defaults to 20 providers. Option functions update these values.

## Dependencies and Integration Points
No external dependencies except same-package deprecated DHT aliases. Consumed by RoutingAPI and routing tests.

## Risks and Test Signals
Risks include type aliases still named `DhtProvideSettings`, offline put bypass, and provider count bounds left to implementations. Tests cover offline put requiring `AllowOffline`, provider search counts, and explicit provide.
