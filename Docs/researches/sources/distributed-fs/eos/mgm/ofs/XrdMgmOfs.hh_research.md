# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfs.hh

## Purpose
`XrdMgmOfs.hh` declares the EOS MGM XRootD OFS plugin class and its large integration surface. It is the central contract for metadata operations, proc/fsctl dispatch, namespace access, authorization, monitoring, service lifecycle, FUSEX broadcasts, traffic shaping, tape support, bulk requests, audit decisions, and global MGM runtime state.

## Important APIs, Types, And Functions
The file defines `NamespaceState` and `namespaceStateToString()`, then declares `class XrdMgmOfs : public XrdSfsFileSystem, public eos::common::LogId`. Public XRootD-facing overrides include `newDir()`, `newFile()`, `Disc()`, `chmod()`, `chksum()`, `exists()`, `FSctl()`, `fsctl()`, `getStats()`, `getVersion()`, `mkdir()`, `FAttr()`, `prepare()`, `rem()`, `remdir()`, `rename()`, `stat()`, `lstat()`, and `truncate()`.

EOS internal APIs include underscored metadata operations such as `_chmod`, `_chown`, `_exists`, `_mkdir`, `_find`, `_rem`, `_remdir`, `_rename`, `_symlink`, `_readlink`, `_stat`, `_access`, `_utimes`, `_touch`, `_attr_ls`, `_attr_set`, `_attr_get`, `_attr_rem`, stripe/replication helpers, versioning helpers, `SendQuery()`, `BroadcastQuery()`, `QueryResync()`, `RemoveDetached()`, sharing helpers, `ApplyMonitoringConfig()`, `GetMonitoringConfig()`, stalling/redirection/routing helpers, path mapping, replica deletion, auth thread methods, FUSEX cast helpers, `SetupProcFiles()`, `OrderlyShutdown()`, `SetRedirectionInfo()`, and audit allow helpers.

Private fsctl/proc dispatch methods include `Access`, `AdjustReplica`, `Checksum`, `Chmod`, `Chown`, `Commit`, `Drop`, `Event`, `FuseStat`, `Fusex`, `Getfmd`, `GetFusex`, `IsMaster`, `Mkdir`, `Open`, `Readlink`, `Redirect`, `Rewrite`, `Statvfs`, `Symlink`, `Utimes`, `Version`, `Xattr`, and `dispatchSFS_FSCTL_PLUGIO()`.

## Control Flow
The header documents the MGM operation pattern: public OFS methods map XRootD client identities to EOS `VirtualIdentity`, apply path mapping, authorization, stall, redirect, and routing macros, then delegate to underscored internal methods that operate on EOS identities and namespace services. Many command bodies are compiled from `ofs/cmds/*.inc`, but their declarations and shared state live here.

Service lifecycle is represented by constructor/destructor plus `Configure()`, `Init()`, `SetupProcFiles()`, and `OrderlyShutdown()`. Threaded subsystems are represented by `AssistedThread` members and worker methods for stats, filesystem config, filesystem monitor, auth master/workers, error logging, and archive submission.

## State And Persistence Behavior
The class owns or references nearly all MGM runtime state: config engine and paths, manager identity, namespace services/views/accounting, namespace state and boot ids, global `MgmStats`, IO stats, traffic-shaping engine, auth plugins and stats, ZMQ context, HTTP/gRPC/REST/WNC servers, Prometheus exporter state, FsView-related locks, routing/path maps, drain/converter/fsck/geotree/recycler/LRU/WFE/device/tape/bulk request engines, QuarkDB contact data, request tracker, pending backup queue, object maps for open files/directories, audit environment flags, and buffer pools.

Some fields correspond to persisted or externally durable locations: namespace changelogs, metadata log directory, proc paths, archive paths, auth token directory, IO report store, temporary find store, comment logs, audit logs, QuarkDB contact/client details, and bulk request proc locations. The header itself does not persist data, but it exposes the ownership and configuration surfaces used by implementation files.

## Dependencies And Integration Points
The header integrates XRootD SFS/OFS interfaces, EOS common utilities, auth protobufs, namespace metadata interfaces and locks, MGM proc/admin commands, traffic shaping, inflight tracking, drain/converter/fsck/geotree/FUSEX/tape/bulk/rest/http/grpc subsystems, QuarkDB namespace contact details, and monitoring. It also declares the global `extern XrdMgmOfs* gOFS`, which many MGM components use as their singleton access point.

## Risks And Edge Cases
This class is broad and stateful, so lock ordering and lifetime are critical. The file-level comments define mutex ordering across FsView, namespace, and quota locks; violating that order can deadlock. Many methods depend on `gOFS`, raw service pointers, and initialized namespace state. The mix of raw pointers, `unique_ptr`, atomics, XRootD buffer ownership, pthread ids, and assisted threads makes partial initialization and shutdown ordering risky. Public/internal method pairs can drift if macro-mediated path, auth, stall, or redirect behavior changes in only one path.

## Test Signals
Tests should cover public-to-internal operation routing, identity mapping and authorization boundaries, lock-order-sensitive metadata mutations, namespace boot/failure states, service startup/shutdown order, path mapping/routing, stall/redirect behavior, fsctl dispatch commands, FUSEX broadcasts, attribute and audit behavior, quota-affecting rename/remove flows, stripe replication/drop operations, query/resync helpers, monitoring reconfiguration, traffic-shaping engine lifetime, and singleton-dependent components during boot and teardown.
