<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/datastore.go -->
# sources/distributed-fs/ipfs-kubo/plugin/datastore.go

## Purpose

This file defines the interface for datastore plugins that add repo datastore backends.

## Important APIs, Types, and Functions

`PluginDatastore` embeds `Plugin` and requires `DatastoreTypeName` and `DatastoreConfigParser`.

## Control Flow, State, and Integration

During plugin injection, the loader registers each parser with `fsrepo.AddDatastoreConfigHandler`, allowing repo configs to instantiate backend-specific datastores.

## Dependencies, Risks, and Test Signals

Dependency is `repo/fsrepo`. Risks include type-name collisions and parser errors making repos unloadable. Datastore plugin tests and repo open/init paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/datastore.go -->
